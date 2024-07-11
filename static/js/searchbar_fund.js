$(document).ready(function() {
    $('#searchInputFund').keyup(function() {
      var searchText = $(this).val().toLowerCase();
  
      // Filter table rows based on the search input
      $('tbody tr').each(function() {
        var fundDate = $(this).find('td:nth-child(1)').text().toLowerCase();
  
        // Parse the fundDate string into a Date object
        var fundDateObj = new Date(fundDate);
  
        // Format the fundDate as YYYY-MM-DD
        var formattedFundDate = fundDateObj.toISOString().split('T')[0];
  
        if (formattedFundDate.includes(searchText)) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });
    });
  });