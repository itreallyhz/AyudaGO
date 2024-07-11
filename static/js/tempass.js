const approveButtons = document.getElementsByClassName('approve');

for (let i = 0; i < approveButtons.length; i++) {
  approveButtons[i].addEventListener('click', (e) => {
    e.preventDefault();

    const row = e.target.closest('tr');
    const firstName = row.querySelector('.first-name').textContent;
    const middleName = row.querySelector('.middle-name').textContent;
    const lastName = row.querySelector('.last-name').textContent;
    const userEmail = row.querySelector('.user-email').textContent;
    const userId = e.target.getAttribute('data-user-id');

    // Generate a random temporary password
    const temporaryPassword = generateTemporaryPassword(8);

    let emailBody = `
      Good Day! Madam/ Sir <b>${firstName} ${middleName} ${lastName}</b>, we extend our gratitude for registering an account on AyudaGo. <br>
      Here's your Temporary Password: <b>${temporaryPassword}</b>
    `;

    Email.send({
      SecureToken: "4f8d5b81-06e5-43e5-9ba3-c88091d76471", // Add your token here
      To: userEmail,
      From: "ayudagoph2023@gmail.com",
      Subject: "AyudaGo: Temporary Password",
      Body: emailBody
    }).then(message => {
      // Send a GET request to the approval route
      fetch(`/approve_user/${userId}?user_password=${encodeURIComponent(temporaryPassword)}`, { method: 'GET' })

        .then(response => {
          if (response.ok) {
            // Redirect to the success page after the approval
            window.location.href = '/accounts';
          } else {
            // Handle error response
            console.error('Error approving user');
          }
        });
    });
  });
}

function generateTemporaryPassword(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let password = '';
  for (let i = 0; i < length; i++) {
    password += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return password;
}