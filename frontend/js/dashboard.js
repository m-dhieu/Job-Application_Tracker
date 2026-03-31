// Dashboard page script

// Backend base URL
var BASE_URL = "http://localhost:8080";

// Logout function
function logout() {
  // Clear any stored session data
  localStorage.removeItem('access_token');
  sessionStorage.removeItem('access_token');
  localStorage.removeItem('user_id');
  sessionStorage.removeItem('user_id');

  // Redirect to login page
  window.location.href = '/static/log-in.html';
}

// Sidebar navigation elements
var navDashboard = document.getElementById('nav-dashboard');
var navApplications = document.getElementById('nav-applications');
var navJobSearch = document.getElementById('nav-job-search');
var navCvReview = document.getElementById('nav-cv-review');
var navEssayReview = document.getElementById('nav-essay-review');

// Section references
var dashboardSection = document.getElementById('dashboard-section');
var cvReviewSection = document.getElementById('cv-review-section');
var essayReviewSection = document.getElementById('essay-review-section');
var jobSearchSection = document.getElementById('job-search-section');

// Array of all nav items for managing active state
var navItems = [navDashboard, navApplications, navJobSearch, navCvReview, navEssayReview];

// Function to show only the selected section and hide others
function showSection(sectionId) {
  dashboardSection.style.display = 'none';
  cvReviewSection.style.display = 'none';
  essayReviewSection.style.display = 'none';
  jobSearchSection.style.display = 'none';

  if (sectionId === 'dashboard') {
    dashboardSection.style.display = '';
  } else if (sectionId === 'cvReview') {
    cvReviewSection.style.display = 'block';
  } else if (sectionId === 'essayReview') {
    essayReviewSection.style.display = 'block';
  } else if (sectionId === 'jobSearch') {
    jobSearchSection.style.display = 'block';
  }
}

// Function to set the 'active' class on the clicked nav item and remove from others
function setActiveNav(clickedNav) {
  navItems.forEach(function(item) {
    if (item) {
      item.classList.remove('active');
    }
  });
  if (clickedNav) {
    clickedNav.classList.add('active');
  }
}

// Attach click event listeners for sidebar navigation items
if (navDashboard) {
  navDashboard.addEventListener('click', function() {
    setActiveNav(navDashboard);
    showSection('dashboard');
  });
}

if (navApplications) {
  navApplications.addEventListener('click', function() {
    setActiveNav(navApplications);
    showSection('dashboard'); // Show dashboard section but load job applications
    loadJobApplications();
  });
}

if (navCvReview) {
  navCvReview.addEventListener('click', function() {
    setActiveNav(navCvReview);
    showSection('cvReview');
  });
}

if (navEssayReview) {
  navEssayReview.addEventListener('click', function() {
    setActiveNav(navEssayReview);
    showSection('essayReview');
  });
}

if (navJobSearch) {
  navJobSearch.addEventListener('click', function() {
    setActiveNav(navJobSearch);
    showSection('jobSearch');
  });
}

// Initially show the dashboard section and load job applications
showSection('dashboard');
loadJobApplications();

// Add keyboard support for job filters
document.addEventListener('DOMContentLoaded', function() {
  // Add Enter key support for filter inputs
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
      var target = event.target;
      if (target.id === 'job-keyword-filter' || target.id === 'job-status-filter') {
        applyJobFilters();
      }
    }
  });
});

// --- Job Applications: Load real job data ---

// Store the original job data for filtering
var originalJobsData = [];

function loadJobApplications() {
  var applicationsBody = document.getElementById('applications-body');

  if (!applicationsBody) {
    console.error('Applications table body not found');
    return;
  }

  // Show loading state
  applicationsBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: #6b7a90;">🔄 Loading latest job opportunities...</td></tr>';

  // Fetch jobs from the API
  fetch(BASE_URL + '/api/jobs?limit=25&offset=0')
    .then(function(response) {
      if (!response.ok) {
        throw new Error('Failed to fetch jobs: ' + response.statusText);
      }
      return response.json();
    })
    .then(function(data) {
      console.log('Job opportunities data:', data);

      if (data.jobs && data.jobs.length > 0) {
        // Store original data for filtering
        originalJobsData = data.jobs.map(function(job, index) {
          // Generate more realistic statuses based on job posting freshness
          var statuses = [
            'Available', 'New Posting', 'Hot', 'Recently Posted', 'Open', 
            'Trending', 'Remote Available', 'Urgent', 'Featured'
          ];
          var randomStatus = statuses[Math.floor(Math.random() * statuses.length)];

          // Use the actual job posting date or generate recent dates
          var jobDate;
          if (job.created_at) {
            jobDate = new Date(job.created_at).toLocaleDateString('en-US', {
              month: '2-digit',
              day: '2-digit',
              year: 'numeric'
            });
          } else {
            // Generate dates from the last 7 days
            var randomDate = new Date();
            randomDate.setDate(randomDate.getDate() - Math.floor(Math.random() * 7));
            jobDate = randomDate.toLocaleDateString('en-US', {
              month: '2-digit',
              day: '2-digit',
              year: 'numeric'
            });
          }

          // Return enhanced job object
          return {
            ...job,
            status: randomStatus,
            dateFormatted: jobDate,
            companyDisplay: job.companyName || job.company || 'Company',
            titleDisplay: job.title && job.title.length > 50 ? job.title.substring(0, 47) + '...' : (job.title || 'Position Available')
          };
        });

        // Display all jobs initially
        displayFilteredJobs(originalJobsData);
      } else {
        applicationsBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: #6b7a90;">No job opportunities found.</td></tr>';
      }
    })
    .catch(function(error) {
      console.error('Error loading job opportunities:', error);
      applicationsBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: #d32f2f;">❌ Error loading job opportunities: ' + error.message + '</td></tr>';
    });
}

function displayFilteredJobs(jobs) {
  var applicationsBody = document.getElementById('applications-body');

  if (jobs.length === 0) {
    applicationsBody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: #6b7a90;">No jobs match your filter criteria.</td></tr>';
    return;
  }

  // Store current filtered jobs for modal access
  window.currentFilteredJobs = jobs;

  var tableRows = jobs.map(function(job, index) {
    return '<tr style="cursor: pointer; transition: background-color 0.2s;" onmouseover="this.style.backgroundColor=\'#f7faff\'" onmouseout="this.style.backgroundColor=\'\'" onclick="showJobDetails(' + index + ')">' +
      '<td><strong>' + job.companyDisplay + '</strong></td>' +
      '<td>' + job.titleDisplay + '</td>' +
      '<td><span style="color: #4a90e2; font-weight: 500;">' + job.status + '</span></td>' +
      '<td>' + job.dateFormatted + '</td>' +
      '<td class="arrow">&gt;</td>' +
      '</tr>';
  }).join('');

  applicationsBody.innerHTML = tableRows;
}

// Filter functionality
function toggleFilterPanel() {
  var filterPanel = document.getElementById('filter-panel');
  if (filterPanel.style.display === 'none') {
    filterPanel.style.display = 'block';
  } else {
    filterPanel.style.display = 'none';
  }
}

function applyJobFilters() {
  var keywordInput = document.getElementById('job-keyword-filter');
  var statusInput = document.getElementById('job-status-filter');

  var keyword = keywordInput ? keywordInput.value.toLowerCase().trim() : '';
  var status = statusInput ? statusInput.value.trim() : '';

  var filteredJobs = originalJobsData.filter(function(job) {
    var keywordMatch = keyword === '' || 
      (job.titleDisplay.toLowerCase().indexOf(keyword) !== -1) ||
      (job.companyDisplay.toLowerCase().indexOf(keyword) !== -1);

    var statusMatch = status === '' || job.status === status;

    return keywordMatch && statusMatch;
  });

  console.log('Filtered jobs:', filteredJobs.length + ' out of ' + originalJobsData.length);
  displayFilteredJobs(filteredJobs);
}

function clearJobFilters() {
  var keywordInput = document.getElementById('job-keyword-filter');
  var statusInput = document.getElementById('job-status-filter');

  if (keywordInput) keywordInput.value = '';
  if (statusInput) statusInput.value = '';

  // Hide filter panel
  var filterPanel = document.getElementById('filter-panel');
  if (filterPanel) {
    filterPanel.style.display = 'none';
  }
}

// --- Job Search: Filter and sorting logic ---

// Function to sort jobs based on the created_at date in ascending or descending order
function sortJobs(jobs, sortOrder) {
  if (sortOrder === 'date_desc') {
    return jobs.sort(function(a, b) {
      return new Date(b.created_at) - new Date(a.created_at);
    });
  } else if (sortOrder === 'date_asc') {
    return jobs.sort(function(a, b) {
      return new Date(a.created_at) - new Date(b.created_at);
    });
  } else {
    return jobs;
  }
}

// Function to filter jobs based on keyword (title or company) and location matching
function filterJobs(jobs, keyword, location) {
  keyword = keyword.toLowerCase();
  location = location.toLowerCase();

  return jobs.filter(function(job) {
    var title = (job.title || '').toLowerCase();
    var company = (job.company_name || '').toLowerCase();
    var jobLocation = (job.location || '').toLowerCase();

    var keywordMatch = keyword === '' || title.indexOf(keyword) !== -1 || company.indexOf(keyword) !== -1;
    var locationMatch = location === '' || jobLocation.indexOf(location) !== -1;

    return keywordMatch && locationMatch;
  });
}


// Function to render job listings inside the given container element
function renderJobs(jobs, container) {
  if (jobs.length === 0) {
    container.innerHTML = '<p>No jobs match your criteria.</p>';
    return;
  }

  var html = jobs.map(function(job, index) {
    return (
      '<div style="border-bottom: 1px solid #ddd; padding: 10px 0;">' +
        '<strong>' + (job.title || 'No Title') + '</strong><br/>' +
        (job.company_name || 'Unknown Company') + ' — ' + (job.location || 'Location Unknown') + '<br/>' +
        '<small>Posted on: ' + (new Date(job.created_at).toLocaleDateString() || 'N/A') + '</small><br/>' +
        '<div style="margin-top: 8px; display: flex; gap: 12px;">' +
          '<a href="' + job.url + '" target="_blank" rel="noopener noreferrer" style="color: #4a90e2; text-decoration: none;">View Details</a>' +
          '<button onclick="openResourcesModal(\'' + encodeURIComponent(JSON.stringify(job)) + '\')" style="background: #28a745; color: white; border: none; padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 0.9rem;">📚 View Resources</button>' +
        '</div>' +
      '</div>'
    );
  }).join('');

  container.innerHTML = html;
}

// Asynchronous function to fetch jobs from backend, filter, sort, and display them
function searchJobs() {
  var keywordInput = document.getElementById('filter-keyword');
  var locationInput = document.getElementById('filter-location');
  var sortSelect = document.getElementById('sort-order');
  var resultsDiv = document.getElementById('job-search-results');
  if (!keywordInput || !locationInput || !sortSelect || !resultsDiv) {
    alert('Job search elements missing in DOM');
    return;
  }

  var keyword = keywordInput.value.trim();
  var location = locationInput.value.trim();
  var sortOrder = sortSelect.value;

  resultsDiv.innerHTML = '<p>Loading jobs...</p>';

  // Fetch jobs from backend API
  fetch(BASE_URL + '/api/jobs/?limit=50&offset=0')
    .then(function(response) {
      if (!response.ok) {
        throw new Error('Server error: ' + response.statusText);
      }
      return response.json();
    })
    .then(function(data) {
      console.log('Fetched raw jobs data:', data);

      var jobsList = [];
      if (Array.isArray(data)) {
        jobsList = data;
      } else if (data.jobs && Array.isArray(data.jobs)) {
        jobsList = data.jobs;
      } else {
        jobsList = Object.values(data);
      }

      console.log('Processed jobsList:', jobsList);

      // Filter and sort jobs before rendering
      var filteredJobs = sortJobs(filterJobs(jobsList, keyword, location), sortOrder);
      console.log('Filtered and sorted jobs:', filteredJobs);
      renderJobs(filteredJobs, resultsDiv);
    })
    .catch(function(error) {
      console.error('Error fetching or processing jobs:', error);
      resultsDiv.innerHTML = '<p style="color: red;">Error loading jobs: ' + error.message + '</p>';
    });
}

// Attach event listener to the job search button to trigger the search
var searchJobsBtn = document.getElementById('search-jobs-btn');
if (searchJobsBtn) {
  searchJobsBtn.addEventListener('click', function() {
    var keywordInputVal = document.getElementById('filter-keyword').value.trim();
    var locationInputVal = document.getElementById('filter-location').value.trim();

    if (keywordInputVal === '' && locationInputVal === '') {
      alert('Please enter a keyword or location to search jobs.');
      return;
    }
    searchJobs();
  });
} else {
  console.warn('Search jobs button (#search-jobs-btn) not found in DOM.');
}

// --- CV Review upload handler ---

var uploadCvBtn = document.getElementById('upload-cv-btn');
if (uploadCvBtn) {
  uploadCvBtn.addEventListener('click', function() {
    var fileInput = document.getElementById('cv-file-input');
    var resultPre = document.getElementById('cv-review-result');

    if (resultPre) {
      resultPre.textContent = '';
    }

    if (!fileInput) {
      alert('CV file input not found.');
      return;
    }
    if (fileInput.files.length === 0) {
      alert('Please select a CV file to upload.');
      return;
    }

    var formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch(BASE_URL + '/api/cv-review', {
      method: 'POST',
      body: formData
    })
    .then(function(response) {
      if (!response.ok) {
        throw new Error('Server error: ' + response.statusText);
      }
      return response.json();
    })
    .then(function(result) {
      console.log('CV Review result:', result);
      if (resultPre) {
        // Display user-friendly analysis
        if (result.analysis) {
          resultPre.innerHTML = result.analysis.replace(/\n/g, '<br>');
        } else {
          // Fallback to JSON if analysis not available
          resultPre.textContent = JSON.stringify(result, null, 2);
        }
      }
    })
    .catch(function(error) {
      console.error('Error uploading CV:', error);
      if (resultPre) {
        resultPre.textContent = 'Error: ' + error.message;
      }
    });
  });
} else {
  console.warn('Upload CV button (#upload-cv-btn) not found in DOM.');
}

// --- Essay Review Logic ---

var reviewEssayBtn = document.getElementById('review-essay-btn');
if (reviewEssayBtn) {
  reviewEssayBtn.addEventListener('click', function() {
    var textArea = document.getElementById('essay-text');
    var fileInput = document.getElementById('essay-file-input');
    var resultsDiv = document.getElementById('review-results');

    if (!textArea || !fileInput || !resultsDiv) {
      alert('Essay review elements missing.');
      return;
    }

    resultsDiv.innerHTML = '';

    if (fileInput.files.length > 0) {
      var file = fileInput.files[0];
      if (file.type !== 'text/plain') {
        alert('Please upload a valid .txt file for the essay.');
        return;
      }
      var reader = new FileReader();
      reader.onload = function(e) {
        analyzeEssay(e.target.result, resultsDiv);
      };
      reader.readAsText(file);
    } else if (textArea.value.trim().length > 0) {
      analyzeEssay(textArea.value.trim(), resultsDiv);
    } else {
      alert('Please paste your essay text or upload a .txt file.');
    }
  });
} else {
  console.warn('Essay review button (#review-essay-btn) not found in DOM.');
}


// Function to analyze essay text, provide basic statistics and call backend grammar check
function analyzeEssay(text, resultsDiv) {
  // Calculate word count by matching word boundaries
  var wordCount = (text.match(/\b\w+\b/g) || []).length;

  // Calculate sentence count by splitting on punctuation and filtering out empty strings
  var sentences = text.split(/[.!?]+/).filter(function(s) {
    return s.trim().length > 0;
  });
  var sentenceCount = sentences.length;

  // Detect long sentences (more than 30 words)
  var longSentences = sentences.filter(function(s) {
    var wordsInSentence = s.match(/\b\w+\b/g) || [];
    return wordsInSentence.length > 30;
  });

  // Frequency count of all words (case-insensitive)
  var words = text.toLowerCase().match(/\b\w+\b/g) || [];
  var freq = {};
  words.forEach(function(word) {
    if (!freq[word]) {
      freq[word] = 0;
    }
    freq[word]++;
  });

  // Find words repeated more than 5 times
  var repeatedWords = [];
  for (var word in freq) {
    if (freq[word] > 5) {
      repeatedWords.push(word);
    }
  }

  // Build initial output HTML with statistics
  var output = '<strong>Word count:</strong> ' + wordCount + '<br/>';
  output += '<strong>Sentence count:</strong> ' + sentenceCount + '<br/>';
  output += '<strong>Long sentences detected:</strong> ' + (longSentences.length > 0 ? longSentences.length : 'None') + '<br/>';
  output += '<strong>Frequently repeated words:</strong> ' + (repeatedWords.length > 0 ? repeatedWords.join(', ') : 'None') + '<br/>';

  resultsDiv.innerHTML = output + '<hr/><em>Checking grammar via backend...</em>';

  // Call backend API for grammar check
  fetch(BASE_URL + '/api/grammar-check', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: text })
  })
  .then(function(response) {
    if (!response.ok) {
      throw new Error('Grammar check failed: ' + response.statusText);
    }
    return response.json();
  })
  .then(function(grammarResult) {
    console.log('Grammar check result:', grammarResult);

    // Handle the new enhanced grammar response format
    if (grammarResult.suggestions && grammarResult.suggestions.length > 0) {
      var issuesHtml = grammarResult.suggestions.map(function(suggestion) {
        var correctionsHtml = '';
        if (suggestion.possible_corrections && suggestion.possible_corrections.length > 0) {
          correctionsHtml = '<br><strong>Possible corrections:</strong> ' + 
            suggestion.possible_corrections.map(function(correction) {
              return '<code>' + correction + '</code>';
            }).join(', ');
        }

        return '<li>' +
          '<strong>' + suggestion.error_type + ':</strong> ' + suggestion.short_message + 
          '<br><strong>Error:</strong> "<span style="background-color: #ffebee; padding: 2px 4px;">' + suggestion.error_text + '</span>"' +
          '<br><strong>Context:</strong> "' + suggestion.context + '"' +
          correctionsHtml +
          '</li>';
      }).join('');

      resultsDiv.innerHTML += '<h4>Grammar Suggestions (' + grammarResult.total_errors + ' issue(s)):</h4><ul style="margin-left: 20px;">' + issuesHtml + '</ul>';
    } else {
      resultsDiv.innerHTML += '<h4>Grammar Suggestions:</h4><p style="color: green;">✅ No grammar issues found!</p>';
    }
  })
  .catch(function(error) {
    console.error('Error during grammar check:', error);
    resultsDiv.innerHTML += '<p style="color:red;">Error checking grammar: ' + error.message + '</p>';
  });
}

// --- Job Details Modal Functions ---

function showJobDetails(jobIndex) {
  var jobs = window.currentFilteredJobs || originalJobsData;
  var job = jobs[jobIndex];

  if (!job) {
    console.error('Job not found at index:', jobIndex);
    return;
  }

  // Store current job for apply functionality
  window.currentJob = job;

  // Populate modal fields
  document.getElementById('modal-job-title').textContent = job.title || 'Position Available';
  document.getElementById('modal-company-name').textContent = job.companyDisplay || 'Company';
  document.getElementById('modal-employment-type').textContent = job.employmentType || 'Not specified';
  document.getElementById('modal-status').textContent = job.status || 'Available';

  // Format salary
  var salaryText = 'Not specified';
  if (job.minSalary && job.maxSalary) {
    salaryText = '$' + job.minSalary.toLocaleString() + ' - $' + job.maxSalary.toLocaleString();
    if (job.currency && job.currency !== 'USD') {
      salaryText += ' ' + job.currency;
    }
  } else if (job.minSalary) {
    salaryText = 'From $' + job.minSalary.toLocaleString();
  }
  document.getElementById('modal-salary').textContent = salaryText;

  // Clean and display description
  var description = job.description || job.excerpt || 'No description available.';
  // Remove HTML tags for basic display
  description = description.replace(/<[^>]*>/g, '').trim();
  if (description.length > 500) {
    description = description.substring(0, 497) + '...';
  }
  document.getElementById('modal-description').textContent = description;

  // Display categories
  var categoriesContainer = document.getElementById('modal-categories');
  var categoriesSection = document.getElementById('modal-categories-section');

  if (job.categories && job.categories.length > 0) {
    categoriesSection.style.display = 'block';
    categoriesContainer.innerHTML = job.categories.map(function(category) {
      return '<span style="background: #e6f0fa; color: #183153; padding: 4px 8px; border-radius: 16px; font-size: 0.8rem;">' + category + '</span>';
    }).join('');
  } else {
    categoriesSection.style.display = 'none';
  }

  // Show modal
  document.getElementById('job-modal').style.display = 'block';


  // Prevent body scroll
  document.body.style.overflow = 'hidden';
}

function closeJobModal() {
  document.getElementById('job-modal').style.display = 'none';
  document.body.style.overflow = 'auto';
  window.currentJob = null;
}

function applyToJob() {
  var job = window.currentJob;
  if (!job) {
    alert('No job selected');
    return;
  }

  if (job.applicationLink) {
    // Open the application link in a new tab
    window.open(job.applicationLink, '_blank');

    // Show success message and close modal
    setTimeout(function() {
      alert('Application page opened! Good luck with your application to ' + (job.companyDisplay || 'this company') + '! 🚀');
      closeJobModal();
    }, 500);
  } else {
    alert('Application link not available for this position.');
  }
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
  var modal = document.getElementById('job-modal');
  if (event.target === modal) {
    closeJobModal();
  }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
  if (event.key === 'Escape') {
    var modal = document.getElementById('job-modal');
    var resourcesModal = document.getElementById('resources-modal');
    if (modal && modal.style.display === 'block') {
      closeJobModal();
    }
    if (resourcesModal && resourcesModal.style.display === 'block') {
      closeResourcesModal();
    }
  }
});

// Resources Modal Functions
function openResourcesModal(jobDataEncoded) {
  try {
    var job = JSON.parse(decodeURIComponent(jobDataEncoded));
    var modal = document.getElementById('resources-modal');
    var jobTitleElement = document.getElementById('resources-job-title');
    var loadingElement = document.getElementById('resources-loading');
    var contentElement = document.getElementById('resources-content');

    // Set job title
    jobTitleElement.textContent = 'Skills and resources for: ' + (job.title || 'Unknown Position');

    // Show modal and loading state
    modal.style.display = 'block';
    loadingElement.style.display = 'block';
    contentElement.style.display = 'none';

    // Fetch skills and resources from backend
    fetchJobSkillsAndResources(job);

  } catch (error) {
    console.error('Error opening resources modal:', error);
    alert('Error loading job resources');
  }
}

function closeResourcesModal() {
  var modal = document.getElementById('resources-modal');
  modal.style.display = 'none';
}

function fetchJobSkillsAndResources(job) {
  // Create a job description from available job data
  var jobDescription = [
    job.title || '',
    job.company_name || '',
    job.description || '',
    job.requirements || ''
  ].join(' ');

  // First, try to get skills from the job ID if available
  var skillsUrl = BASE_URL + '/api/jobs/' + (job.id || 'dummy') + '/skills';

  fetch(skillsUrl)
    .then(function(response) {
      if (!response.ok) {
        // If job-specific skills fail, extract from description
        throw new Error('Job skills not available');
      }
      return response.json();
    })
    .then(function(skillsData) {
      displaySkillsAndResources(skillsData.skills || [], skillsData.resources || []);
    })
    .catch(function(error) {
      console.log('Falling back to description-based skill extraction');
      // Fallback: extract skills from job description
      extractSkillsFromDescription(jobDescription);
    });
}

function extractSkillsFromDescription(description) {
  // Define common tech skills to look for
  var commonSkills = [
    'javascript', 'python', 'java', 'react', 'angular', 'vue', 'node.js', 'typescript',
    'html', 'css', 'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'docker',
    'kubernetes', 'git', 'linux', 'machine learning', 'data science', 'artificial intelligence',
    'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'flutter', 'react native',
    'express', 'django', 'flask', 'spring', 'laravel', 'rails', 'selenium', 'jenkins',
    'terraform', 'ansible', 'redis', 'elasticsearch', 'graphql', 'rest api', 'microservices'
  ];

  var foundSkills = [];
  var lowerDescription = description.toLowerCase();

  commonSkills.forEach(function(skill) {
    if (lowerDescription.includes(skill.toLowerCase())) {
      foundSkills.push(skill);
    }
  });

  // If no skills found, add some generic ones
  if (foundSkills.length === 0) {
    foundSkills = ['programming', 'software development', 'problem solving'];
  }

  // Fetch resources for found skills
  fetchResourcesForSkills(foundSkills);
}

function fetchResourcesForSkills(skills) {
  var skillsParam = skills.slice(0, 5).join(','); // Limit to 5 skills
  var resourcesUrl = BASE_URL + '/api/resources/bulk?skills=' + encodeURIComponent(skillsParam);

  fetch(resourcesUrl)
    .then(function(response) {
      if (!response.ok) {
        throw new Error('Failed to fetch resources');
      }
      return response.json();
    })
    .then(function(data) {
      var allResources = [];
      Object.keys(data.resources || {}).forEach(function(skill) {
        if (data.resources[skill] && data.resources[skill].length > 0) {
          allResources = allResources.concat(data.resources[skill].map(function(resource) {
            return Object.assign(resource, { skill: skill });
          }));
        }
      });
      displaySkillsAndResources(skills, allResources);
    })
    .catch(function(error) {
      console.error('Error fetching resources:', error);
      displaySkillsAndResources(skills, []);
    });
}

function displaySkillsAndResources(skills, resources) {
  var loadingElement = document.getElementById('resources-loading');
  var contentElement = document.getElementById('resources-content');
  var skillsContainer = document.getElementById('skills-container');
  var resourcesContainer = document.getElementById('resources-container');

  // Hide loading, show content
  loadingElement.style.display = 'none';
  contentElement.style.display = 'block';

  // Display skills
  skillsContainer.innerHTML = skills.map(function(skill) {
    return '<span style="background: #e3f2fd; color: #1976d2; padding: 6px 12px; border-radius: 16px; font-size: 0.9rem; font-weight: 500;">' + skill + '</span>';
  }).join('');

  // Display resources
  if (resources.length === 0) {
    resourcesContainer.innerHTML = '<p style="color: #6b7a90; font-style: italic;">No specific resources found. Try searching for these skills on popular learning platforms like Coursera, Udemy, or freeCodeCamp.</p>';
  } else {
    resourcesContainer.innerHTML = resources.slice(0, 10).map(function(resource) {
      return (
        '<div style="background: #f7faff; border: 1px solid #e6f0fa; border-radius: 8px; padding: 16px;">' +
          '<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">' +
            '<h4 style="margin: 0; color: #183153; font-size: 1rem;">' + (resource.title || 'Learning Resource') + '</h4>' +
            (resource.skill ? '<span style="background: #4a90e2; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">' + resource.skill + '</span>' : '') +
          '</div>' +
          (resource.description ? '<p style="margin: 8px 0; color: #6b7a90; font-size: 0.9rem; line-height: 1.4;">' + resource.description + '</p>' : '') +
          '<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">' +
            '<a href="' + (resource.url || '#') + '" target="_blank" rel="noopener noreferrer" style="background: #4a90e2; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.9rem;">View Resource</a>' +
            (resource.platform ? '<span style="color: #6b7a90; font-size: 0.8rem;">' + resource.platform + '</span>' : '') +
          '</div>' +
        '</div>'
      );
    }).join('');
  }
}
