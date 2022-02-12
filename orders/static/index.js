document.addEventListener('DOMContentLoaded', () => {

      document.querySelector('#add_folder').disabled = true;
      document.querySelector('#submit_search').disabled = true;

      // Enable new folder button only if there is text in the input field
      document.querySelector('#new_folder').onkeyup = () => {
          if (document.querySelector('#new_folder').value.length > 0)
              document.querySelector('#add_folder').disabled = false;
          else
              document.querySelector('#add_folder').disabled = true;
      };

      // Enable search button only if there is text in the input field
      document.querySelector('#search').onkeyup = () => {
          if (document.querySelector('#search').value.length > 0)
              document.querySelector('#submit_search').disabled = false;
          else
              document.querySelector('#submit_search').disabled = true;
      };
});
