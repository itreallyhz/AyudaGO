
  $(document).ready(function() {
    $('#searchInput').keyup(function() {
      var searchText = $(this).val().toLowerCase();
  
      // Filter table rows based on the search input
      $('tbody tr').each(function() {
        var fullName = $(this).find('td:eq(1)').text().toLowerCase();
      
        if (fullName.includes(searchText)) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    });
  });
