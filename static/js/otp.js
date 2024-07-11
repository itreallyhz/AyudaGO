// const approveButtons = document.getElementsByClassName('click');

// for (let i = 0; i < approveButtons.length; i++) {
//   approveButtons[i].addEventListener('click', (e) => {
//     e.preventDefault();

//     const userEmail = document.querySelector('.user-email').value;

//     // Generate a random OTP code
//     const userOtp = generateOTP(4);

//     let emailBody = `
//       Thank you for using AyudaGo! Here's the OTP code: <b>${userOtp}</b>
//     `;

//     Email.send({
//       SecureToken: "4f8d5b81-06e5-43e5-9ba3-c88091d76471", // Add your token here
//       To: userEmail,
//       From: "ayudagoph2023@gmail.com",
//       Subject: "AyudaGo: Temporary Password",
//       Body: emailBody
//     }).then(message => {
//       // Send a POST request to the server to save OTP
//       fetch(`/code/${encodeURIComponent(userOtp)}`, { method: 'POST' })
//         .then(response => {
//           if (response.ok) {
//             // Redirect to the success page after the approval
//             window.location.href = '/success'; // Redirect to '/success' or another appropriate page
//           } else {
//             // Handle error response
//             console.error('Error');
//           }
//         });
//     });
//   });
// }

// function generateOTP(length) {
//   const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
//   let otp = '';
//   for (let i = 0; i < length; i++) {
//     otp += characters.charAt(Math.floor(Math.random() * characters.length));
//   }
//   return otp;
// }

// const submit = document.getElementById('send');
// const userEmail = document.getElementById('user_email');

// submit.addEventListener('click', (e) => {
//     e.preventDefault();
//     console.log("Clicked");
//     // Generate OTP
//     const otp = generateOTP(4);

//     let ebody = `
//     Here's your <b>OTP Code:${otp}</b>
//     `;

//     // Configure the email options
//     Email.send({
//         SecureToken: "4f8d5b81-06e5-43e5-9ba3-c88091d76471",
//         To: userEmail.value,
//         From: "ayudagoph2023@gmail.com",
//         Subject: "OTP Verification",
//         Body: ebody,
//     }).then(message => {
//        fetch(`/code/${encodeURIComponent(userOtp)}`, { method: 'POST' })
//         .then(response => {
//             if (response.ok) {
//               // Redirect to the success page after the approval
//               window.location.href = '/code';
//             } else {
//               // Handle error response
//               console.error('Error approving user');
//             }
//         });
//     });
// });

// function generateOTP(length) {
//     const code = '123456789';
//     let otp = '';
//     for (let i = 0; i < length; i++) {
//         otp += code.charAt(Math.floor(Math.random() * code.length));
//     }
//     return otp;
// }


// const submit = document.getElementById('send');
// const userEmail = document.getElementById('user_email');

// submit.addEventListener('click', (e) => {
//     e.preventDefault();
//     console.log("Clicked");
//     // Generate OTP
//     const otp = generateOTP(4);

//     let ebody = `
//     Here's your <b>OTP Code:${otp}</b>
//     `;

//     // Configure the email options
//     Email.send({
//         SecureToken: "4f8d5b81-06e5-43e5-9ba3-c88091d76471",
//         To: userEmail.value,
//         From: "ayudagoph2023@gmail.com",
//         Subject: "OTP Verification",
//         Body: ebody,
//     }).then(message => {
//         // Make an HTTP request to fetch the OTP code
//         fetch('/otp')
//             .then(response => response.json())
//             .then(data => {
//                 const otpCode = data.otp_code;
//                 // Redirect to the code page with the OTP code
//                 window.location.href = `/code?otp_code=${otpCode}`;
//             })
//             .catch(error => {
//                 console.error('Error:', error);
//             });
//     });
// });

// function generateOTP(length) {
//     const code = '123456789';
//     let otp = '';
//     for (let i = 0; i < length; i++) {
//         otp += code.charAt(Math.floor(Math.random() * code.length));
//     }
//     return otp;
// }

const submit = document.getElementById('send');
const userEmail = document.getElementById('user_email');

submit.addEventListener('click', (e) => {
    e.preventDefault();
    console.log("Clicked");
    // Generate OTP
    const otp = generateOTP(4);

    let ebody = `
    Here's your <b>OTP Code:${otp}</b>
    `;

    // Configure the email options
    Email.send({
        SecureToken: "4f8d5b81-06e5-43e5-9ba3-c88091d76471",
        To: userEmail.value,
        From: "ayudagoph2023@gmail.com",
        Subject: "OTP Verification",
        Body: ebody,
    }).then(message => {
      window.location.href = `/code/${userEmail.value}/${otp}`;
    });
});



function generateOTP(length) {
    const code = '123456789';
    let otp = '';
    for (let i = 0; i < length; i++) {
        otp += code.charAt(Math.floor(Math.random() * code.length));
    }
    return otp;
}
function validateOTP() {
  const otpInputs = document.getElementsByClassName("otp-input");
  const enteredOTP = Array.from(otpInputs)
      .map(input => input.value)
      .join('');

  if (enteredOTP === otp) {
      document.regForm.submit();
  } else {
      alert("Code does not match. Please try again.");
  }
}