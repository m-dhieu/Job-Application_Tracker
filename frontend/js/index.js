// Landing page script

// Script to enable smooth scrolling to anchor links on the page
// When clicking on any link with a href that starts with "#", the page scrolls smoothly to the target element

// Select all anchor elements with href attribute starting with '#'
const anchorLinks = document.querySelectorAll('a[href^="#"]');

anchorLinks.forEach(function(anchor) {
  // Add click event listener to each anchor link
  anchor.addEventListener('click', function(event) {
    // Prevent the default jump-to-anchor behavior
    event.preventDefault();

    // Get the target element referenced by the href attribute
    const targetID = this.getAttribute('href');
    const targetElement = document.querySelector(targetID);

    // If the target element exists, scroll to it smoothly
    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: 'smooth'
      });
    }
  });
});

