document.addEventListener('DOMContentLoaded', () => {

      // Capture the "click on location" event
      document.querySelector('#d_loc').onclick = (e) => {
          /* Get the text field */
          var copyText = document.getElementById("d_loc");

          /* Select the text field */
          copyText.select();

          /* Copy the text inside the text field */
          document.execCommand("copy");

          /* Alert the copied text */
          alert("Copied the text: " + copyText.value);
      };

      // Capture the "click on username" event
      document.querySelector('#d_un').onclick = (e) => {
          /* Get the text field */
          var copyText = document.getElementById("d_un");

          /* Select the text field */
          copyText.select();

          /* Copy the text inside the text field */
          document.execCommand("copy");

          /* Alert the copied text */
          alert("Copied the text: " + copyText.value);
      };

      // Capture the "click on password" event
      document.querySelector('#d_pw').onclick = (e) => {
          /* Get the text field */
          var copyText = document.getElementById("d_pw");

          /* Select the text field */
          copyText.select();

          /* Copy the text inside the text field */
          document.execCommand("copy");

          /* Alert the copied text */
          alert("Copied the text: " + "************");
      };
});
