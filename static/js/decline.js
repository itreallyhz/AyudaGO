const declineButtons = document.getElementsByClassName('decline');

for (let i = 0; i < declineButtons.length; i++) {
  declineButtons[i].addEventListener('click', (e) => {
    e.preventDefault();

    const row = e.target.closest('tr');
    const firstName = row.querySelector('.first-name').textContent;
    const middleName = row.querySelector('.middle-name').textContent;
    const lastName = row.querySelector('.last-name').textContent;
    const userEmail = row.querySelector('.user-email').textContent;
    const userId = e.target.getAttribute('data-decline-id');

    let emailBody = `
      Good Day! Madam/Sir <b>${firstName} ${middleName} ${lastName}</b>, we regret to inform you that your registration on AyudaGo has been declined. 
    `;

    Email.send({
      SecureToken: "4f8d5b81-06e5-43e5-9ba3-c88091d76471", // Add your token here
      To: userEmail,
      From: "ayudagoph2023@gmail.com",
      Subject: "YOUR REGISTRATION IS DECLINED",
      Body: emailBody
    }).then(message => {
      // Send a DELETE request to the decline route
      fetch(`/decline_user/${userId}`, { method: 'GET' })

        .then(response => {
          if (response.ok) {
            window.location.href = '/accounts';
          } else {
            // Handle error response
            console.error('Error declining user');
          }
        });
    });
  });
}
