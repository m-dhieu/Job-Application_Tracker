// Job Search with Skills

// Global variables
let currentSearchQuery = '';
let currentResults = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Allow Enter key to search
	
document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchJobs();
        }
    });

    // Load trending skills on page load
    loadTrendingSkills();
});

// Search jobs function
async function searchJobs() {
    const searchInput = document.getElementById('searchInput');
    const limitInput = document.getElementById('limitInput');

    const query = searchInput.value.trim();
    const limit = parseInt(limitInput.value) || 10;

    if (!query) {
        showError('Please enter a search query');
        return;
    }

    currentSearchQuery = query;
    showLoading();
    hideError();

    try {
        const response = await fetch(`/api/jobs/search?query=${encodeURIComponent(query)}&limit=${limit}&offset=0`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        currentResults = data;
        displayResults(data);

    } catch (error) {
        console.error('Search error:', error);
        showError(`Failed to search jobs: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Display search results
function displayResults(data) {
    hideLoading();

    const resultsContainer = document.getElementById('resultsContainer');
    const resultsTitle = document.getElementById('resultsTitle');
    const jobCount = document.getElementById('jobCount');
    const skillCount = document.getElementById('skillCount');

    // Update header
    resultsTitle.textContent = `Search Results for "${data.query}"`;
    jobCount.textContent = `${data.total_jobs} jobs found`;
    skillCount.textContent = `${data.skills_analysis.total_unique_skills} unique skills identified`;

    // Display skills analysis
    displaySkillsAnalysis(data.skills_analysis);

    // Display learning resources
    displayLearningResources(data.learning_resources);

    // Display jobs
    displayJobs(data.jobs);

    // Show results container
    resultsContainer.style.display = 'block';
}

// Display skills analysis
function displaySkillsAnalysis(skillsData) {
    const topSkillsContainer = document.getElementById('topSkills');
    const recommendedSkillsContainer = document.getElementById('recommendedSkills');

    // Clear previous content
    topSkillsContainer.innerHTML = '';
    recommendedSkillsContainer.innerHTML = '';

    // Display top skills
    skillsData.top_skills.forEach(skillInfo => {
        const skillTag = document.createElement('div');
        skillTag.className = 'skill-tag';
        skillTag.innerHTML = `
            <span>${skillInfo.skill}</span>
            <span class="skill-demand">${skillInfo.demand}</span>
        `;
        topSkillsContainer.appendChild(skillTag);
    });

    // Display recommended skills
    skillsData.skill_recommendations.forEach(skill => {
        const skillItem = document.createElement('div');
        skillItem.className = 'recommended-skill';
        skillItem.textContent = skill;
        skillItem.onclick = () => searchSkillResources(skill);
        skillItem.style.cursor = 'pointer';
        skillItem.title = `Click to learn more about ${skill}`;
        recommendedSkillsContainer.appendChild(skillItem);
    });
}

// Display learning resources
function displayLearningResources(resources) {
    const resourcesContainer = document.getElementById('learningResources');
    resourcesContainer.innerHTML = '';

    if (Object.keys(resources).length === 0) {
        resourcesContainer.innerHTML = '<p>No learning resources found for the identified skills.</p>';
        return;
    }

    Object.entries(resources).forEach(([skill, skillResources]) => {
        if (skillResources.length === 0) return;

        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'resource-category';

        categoryDiv.innerHTML = `
            <h4>${skill}</h4>
            ${skillResources.map(resource => `
                <div class="resource-item">
                    <div class="resource-title">${resource.title || 'Learning Resource'}</div>
                    <div class="resource-description">${resource.description || resource.snippet || 'No description available'}</div>
                    <a href="${resource.url || resource.link || '#'}" target="_blank" class="resource-link">Learn More →</a>
                </div>
            `).join('')}
        `;

        resourcesContainer.appendChild(categoryDiv);
    });
}

// Display jobs
function displayJobs(jobs) {
    const jobsContainer = document.getElementById('jobsList');
    jobsContainer.innerHTML = '';

    if (jobs.length === 0) {
        jobsContainer.innerHTML = '<p>No jobs found matching your search criteria.</p>';
        return;
    }

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';

        jobCard.innerHTML = `
            <div class="job-header">
                <div class="job-title">${job.title || 'Untitled Position'}</div>
                <div class="job-company">${job.companyName || 'Unknown Company'}</div>
            </div>

            <div class="job-details">
                ${job.employmentType ? `<span>📄 ${job.employmentType}</span>` : ''}
                ${job.salaryMin && job.salaryMax ? 
                    `<span>💰 $${job.salaryMin.toLocaleString()} - $${job.salaryMax.toLocaleString()}</span>` : 
                    (job.salary ? `<span>💰 ${job.salary}</span>` : '')
                }
                ${job.location ? `<span>📍 ${job.location}</span>` : ''}
            </div>

            ${job.description ? `
                <div class="job-description">${job.description}</div>
            ` : ''}

            ${job.required_skills && job.required_skills.length > 0 ? `
                <div class="job-skills">
                    <h5>Required Skills:</h5>
                    <div class="job-skill-tags">
                        ${job.required_skills.slice(0, 6).map(skill => 
                            `<span class="job-skill-tag">${skill}</span>`
                        ).join('')}
                        ${job.required_skills.length > 6 ? 
                            `<span class="job-skill-tag">+${job.required_skills.length - 6} more</span>` : 
                            ''
                        }
                    </div>
                </div>
            ` : ''}

            <div class="job-actions">
                ${job.applicationLink ?
                    `<button class="btn-apply" onclick="applyToJob('${job.applicationLink}')">Apply Now</button>` :
                    `<button class="btn-apply" disabled>No Application Link</button>`
                }
                <button class="btn-save" onclick="saveJob(${JSON.stringify(job).replace(/"/g, '&quot;')})">Save Job</button>
            </div>
        `;

        jobsContainer.appendChild(jobCard);
    });
}

// Apply to job
function applyToJob(applicationLink) {
    if (applicationLink && applicationLink !== '#') {
        window.open(applicationLink, '_blank');
    } else {
        alert('No application link available for this job.');
    }
}

// Save job (placeholder function)
function saveJob(job) {
    // For now, just show an alert. In a real app, this would save to user's account
    alert(`Job "${job.title}" at ${job.companyName} saved! (Feature coming soon)`);
}

// Search skill resources
async function searchSkillResources(skill) {
    try {
        const response = await fetch(`/api/resources?skill=${encodeURIComponent(skill)}`);
        if (response.ok) {
            const data = await response.json();
            displaySkillResourcesModal(skill, data.resources);
        }
    } catch (error) {
        console.error('Error fetching skill resources:', error);
    }
}

// Display skill resources modal (simple implementation)
function displaySkillResourcesModal(skill, resources) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;


    modal.innerHTML = `
        <div style="background: white; padding: 30px; border-radius: 10px; max-width: 500px; max-height: 80vh; overflow-y: auto;">
            <h3>Learning Resources for ${skill}</h3>
            <div style="margin: 20px 0;">
                ${resources.length > 0 ? 
                    resources.map(resource => `
                        <div style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                            <strong>${resource.title || 'Resource'}</strong><br>
                            <p style="margin: 8px 0; color: #666;">${resource.description || resource.snippet || 'No description'}</p>
                            <a href="${resource.url || resource.link || '#'}" target="_blank" style="color: #667eea;">Learn More →</a>
                        </div>
                    `).join('') :
                    '<p>No resources found for this skill.</p>'
                }
            </div>
            <button onclick="this.parentElement.parentElement.remove()" style="background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Close</button>
        </div>
    `;

  document.body.appendChild(modal);

    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
}

// Load trending skills
async function loadTrendingSkills() {
    try {
        const response = await fetch('/api/resources/trending');
        if (response.ok) {
            const data = await response.json();
            console.log('Trending skills loaded:', data);
        }
    } catch (error) {
        console.log('Could not load trending skills:', error);
    }
}

// Show loading
function showLoading() {
    document.getElementById('loadingIndicator').style.display = 'block';
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('errorContainer').style.display = 'none';
}

// Hide loading
function hideLoading() {
    document.getElementById('loadingIndicator').style.display = 'none';
}

// Show error
function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorContainer').style.display = 'block';
    document.getElementById('resultsContainer').style.display = 'none';
    hideLoading();
}

// Hide error
function hideError() {
    document.getElementById('errorContainer').style.display = 'none';
}

// Clear error
function clearError() {
    hideError();
}
