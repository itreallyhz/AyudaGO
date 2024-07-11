
  // Function to handle the click event of the "Proceed" button
  function handleProceed() {
    // Display the message on the fund status page
    document.getElementById("status-message").innerText = "Your ayuda is ready to claim";
    
    // Show the "Claimed" button
    document.getElementById("claim-button").style.display = "block";
  }
  
  // Add an event listener to the "Proceed" button
  document.getElementById("proceed-button").addEventListener("click", handleProceed);

