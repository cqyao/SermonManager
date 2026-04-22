document.addEventListener('DOMContentLoaded', function() {
  const carousel = document.getElementById('mainCarousel');
  const prevControl = document.querySelector('.carousel__control.left');
  const nextControl = document.querySelector('.carousel__control.right');
  
  const scrollAmount = carousel.offsetWidth; // Scroll by one carousel width
  
  // Function to update arrow visibility
  function updateArrowVisibility() {
    const isAtStart = carousel.scrollLeft === 0;
    const isAtEnd = carousel.scrollLeft + carousel.offsetWidth >= carousel.scrollWidth - 10; // 10px tolerance
    
    if (isAtStart) {
      prevControl.style.opacity = '0.3';
      prevControl.style.pointerEvents = 'none';
    } else {
      prevControl.style.opacity = '1';
      prevControl.style.pointerEvents = 'auto';
    }
    
    if (isAtEnd) {
      nextControl.style.opacity = '0.3';
      nextControl.style.pointerEvents = 'none';
    } else {
      nextControl.style.opacity = '1';
      nextControl.style.pointerEvents = 'auto';
    }
  }
  
  // Initialize arrow visibility
  updateArrowVisibility();
  
  // Update visibility on scroll
  carousel.addEventListener('scroll', updateArrowVisibility);
  
  prevControl.addEventListener('click', function(e) {
    e.preventDefault();
    carousel.scrollBy({
      left: -scrollAmount,
      behavior: 'smooth'
    });
    setTimeout(updateArrowVisibility, 600); // Update after scroll animation
  });
  
  nextControl.addEventListener('click', function(e) {
    e.preventDefault();
    carousel.scrollBy({
      left: scrollAmount,
      behavior: 'smooth'
    });
    setTimeout(updateArrowVisibility, 600); // Update after scroll animation
  });
});