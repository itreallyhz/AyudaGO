document.getElementById("login-button").addEventListener("click", async function(event) {
    event.preventDefault(); // prevent the form from submitting normally
  
    const form = document.getElementById("login-form");
    const data = new URLSearchParams(new FormData(form)); // convert form data to URL-encoded format
  
    const response = await fetch(form.action, {
      method: form.method,
      body: data,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
  
    if (response.redirected) {
      window.location.href = response.url; // redirect to the appropriate page
    } else {
      const result = await response.json();
      alert(result.message); // display error message
    }
  });