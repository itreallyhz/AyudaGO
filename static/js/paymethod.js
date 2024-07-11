// function highlightButton(button) {
//   var buttons = document.getElementsByClassName("border");
  
//   // Remove the highlight class from all buttons
//   for (var i = 0; i < buttons.length; i++) {
//     buttons[i].classList.remove("highlight");
//   }
  
//   // Add the highlight class to the clicked button
//   button.classList.add("highlight");
// }

function showModal(modalId) {
  var modal = document.getElementById(modalId);
  modal.style.display = "block"; // Show the modal
}

document.addEventListener("DOMContentLoaded", function() {
  // Add event listeners to the buttons
  var paypalButton = document.getElementById("paypal-button");
  paypalButton.addEventListener("click", function() {
    showModal("paypal-modal");
  });

  var gcashButton = document.getElementById("gcash-button");
  gcashButton.addEventListener("click", function() {
    showModal("gcash-modal");
  });

  var paymayaButton = document.getElementById("paymaya-button");
  paymayaButton.addEventListener("click", function() {
    showModal("paymaya-modal");
  });

  var bankcardButton = document.getElementById("bankcard-button");
  bankcardButton.addEventListener("click", function() {
    showModal("bankcard-modal");
  });
});