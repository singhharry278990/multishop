$(function () {
    $("#contactForm input, #contactForm textarea").jqBootstrapValidation({
      preventSubmit: true,
      submitError: function ($form, event, errors) {
        // Handle submit errors if needed
      },
      submitSuccess: function ($form, event) {
        event.preventDefault();
        var name = $("input#name").val();
        var email = $("input#email").val();
        var subject = $("input#subject").val();
        var message = $("textarea#message").val();
  
        $this = $("#sendMessageButton");
        $this.prop("disabled", true);
  
        $.ajax({
          url: "/contact/",  // Replace with the actual URL of your Django view
          type: "POST",
          data: {
            name: name,
            email: email,
            subject: subject,
            message: message
          },
          headers: {
            "X-CSRFToken": getCookie("csrftoken")  // Include the CSRF token in the request headers
          },
          cache: false,
          success: function (response) {
            $('#success').html("<div class='alert alert-success'>");
            $('#success > .alert-success').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
              .append("</button>");
            $('#success > .alert-success')
              .append("<strong>" + response.message + "</strong>");
            $('#success > .alert-success')
              .append('</div>');
            $('#contactForm').trigger("reset");
          },
          error: function (xhr, status, error) {
            $('#success').html("<div class='alert alert-danger'>");
            $('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
              .append("</button>");
            $('#success > .alert-danger').append($("<strong>").text("Sorry " + name + ", an error occurred. Please try again later!"));
            $('#success > .alert-danger').append('</div>');
            $('#contactForm').trigger("reset");
          },
          complete: function () {
            setTimeout(function () {
              $this.prop("disabled", false);
            }, 1000);
          }
        });
      },
      filter: function () {
        return $(this).is(":visible");
      },
    });
  
    $("a[data-toggle=\"tab\"]").click(function (e) {
      e.preventDefault();
      $(this).tab("show");
    });
  
    $('#name').focus(function () {
      $('#success').html('');
    });
  
    // Function to get the value of a cookie by name
    function getCookie(name) {
      var cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
          var cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  });
  