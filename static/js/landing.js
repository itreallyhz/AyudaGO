// JavaScript code to create a slideshow
var slides = document.getElementsByClassName("slide");
var currentSlideIndex = 0;

function showSlide(index) {
  if (index < 0) {
    index = slides.length - 1;
  } else if (index >= slides.length) {
    index = 0;
  }

  for (var i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }

  slides[index].style.display = "block";
  currentSlideIndex = index;
}

// Initial slide display
showSlide(currentSlideIndex);

// Automatic slideshow animation
setInterval(function() {
  currentSlideIndex++;
  showSlide(currentSlideIndex);
}, 3000); // Change slide every 3 seconds