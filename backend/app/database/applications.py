from typing import Optional, List, Dict, Any
from datetime import datetime
from .connection import get_connection

class ApplicationManager:
    """Handle job application-related database operations"""

    def create_job_application(self, user_id: int, application_data: Dict[str, Any]) -> Optional[int]:
        """Create a new job application"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO job_applications 
                    (user_id, job_title, company_name, job_url, status, notes, salary_range, 
                     location, employment_type, source, external_job_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    application_data.get('job_title'),
                    application_data.get('company_name'),
                    application_data.get('job_url'),
                    application_data.get('status', 'applied'),
                    application_data.get('notes'),
                    application_data.get('salary_range'),
                    application_data.get('location'),
                    application_data.get('employment_type'),
                    application_data.get('source', 'manual'),
                    application_data.get('external_job_id')
                ))

                application_id = cursor.lastrowid

                # Add initial status history
                cursor.execute('''
                    INSERT INTO application_status_history (application_id, status, notes)
                    VALUES (?, ?, ?)
                ''', (application_id, application_data.get('status', 'applied'), 'Application created'))

                conn.commit()
                return application_id
        except Exception as e:
            print(f"Error creating application: {e}")
            return None

    def get_user_applications(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all applications for a user"""
        with get_connection() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT * FROM job_applications 
                WHERE user_id = ?
            '''
            params = [user_id]

            if status:
                query += ' AND status = ?'
                params.append(status)

            query += ' ORDER BY application_date DESC'

            cursor.execute(query, params)
            applications = cursor.fetchall()

            return [dict(app) for app in applications]

    def get_application_by_id(self, application_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific application by ID"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM job_applications 
                WHERE id = ? AND user_id = ?
            ''', (application_id, user_id))

            application = cursor.fetchone()
            return dict(application) if application else None

    def update_application_status(self, application_id: int, user_id: int, new_status: str, notes: str = None) -> bool:
        """Update application status"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Verify application belongs to user
                cursor.execute('''
                    SELECT id FROM job_applications WHERE id = ? AND user_id = ?
                ''', (application_id, user_id))

                if not cursor.fetchone():
                    return False

                # Update application status
                cursor.execute('''
                    UPDATE job_applications SET status = ? WHERE id = ?
                ''', (new_status, application_id))

                # Add status history
                cursor.execute('''
                    INSERT INTO application_status_history (application_id, status, notes)
                    VALUES (?, ?, ?)
                ''', (application_id, new_status, notes))

                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating application status: {e}")
            return False

    def update_application(self, application_id: int, user_id: int, update_data: Dict[str, Any]) -> bool:
        """Update application details"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()

                # Verify application belongs to user
                cursor.execute('''
                    SELECT id FROM job_applications WHERE id = ? AND user_id = ?
                ''', (application_id, user_id))

                if not cursor.fetchone():
                    return False

                # Build dynamic update query
                fields = []
                values = []
                allowed_fields = ['job_title', 'company_name', 'job_url', 'notes', 'salary_range', 
                                'location', 'employment_type', 'source', 'external_job_id']

                for key, value in update_data.items():
                    if key in allowed_fields:
                        fields.append(f"{key} = ?")
                        values.append(value)

                if fields:
                    values.append(application_id)
                    values.append(user_id)

                    query = f"UPDATE job_applications SET {', '.join(fields)} WHERE id = ? AND user_id = ?"
                    cursor.execute(query, values)
                    conn.commit()

                return True
        except Exception as e:
            print(f"Error updating application: {e}")
            return False

    def delete_application(self, application_id: int, user_id: int) -> bool:
        """Delete a job application"""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM job_applications WHERE id = ? AND user_id = ?
                ''', (application_id, user_id))

                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting application: {e}")
            return False

    def get_application_history(self, application_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get status history for an application"""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ash.* FROM application_status_history ash
                JOIN job_applications ja ON ash.application_id = ja.id
                WHERE ash.application_id = ? AND ja.user_id = ?
                ORDER BY ash.changed_at DESC
            ''', (application_id, user_id))

            history = cursor.fetchall()
            return [dict(record) for record in history]

    def get_application_stats(self, user_id: int) -> Dict[str, Any]:
        """Get application statistics for a user"""
        applications = self.get_user_applications(user_id)

        # Calculate statistics
        total_applications = len(applications)
        status_counts = {}

        for app in applications:
            status = app['status']
            status_counts[status] = status_counts.get(status, 0) + 1

        # Calculate this month's applications
        current_month = datetime.now().replace(day=1)
        this_month_count = sum(
            1 for app in applications 
            if datetime.fromisoformat(app['application_date'].replace('Z', '+00:00')).replace(tzinfo=None) >= current_month
        )

        return {
            "total_applications": total_applications,
            "status_breakdown": status_counts,
            "this_month": this_month_count,
            "response_rate": round(
                (status_counts.get('interviewing', 0) + status_counts.get('accepted', 0)) / max(total_applications, 1) * 100, 1
            )
        }
