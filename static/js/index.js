function getBotResponse() {
    var rawText = $("#textInput").val();
    // var bot = {}
    //bot.avatar = "https//"
    // var user = {}
    //user.avatar = "https//"
    var userHtml = '<p class="userText"><img class="img-circle avatar" style="width:10%;" src="./static/icon.jpg" /><span>' + rawText + '</span></p>';
    $("#textInput").val("");
    $("#chatbox").append(userHtml);
    document.getElementById('userInput').scrollIntoView({block: 'start', behavior: 'smooth'});
    $.get("/get", { msg: rawText }).done(function(data) {
      var botHtml = '<p class="botText"><img class=" img-circle avatar" style="width:10%;" src="./static/icon2.jpg" /><span>' + data + '</span></p>';
      $("#chatbox").append(botHtml);
      document.getElementById('userInput').scrollIntoView({block: 'start', behavior: 'smooth'});
    });
  }
  $("#textInput").keypress(function(e) {
      if(e.which == 13) {
          getBotResponse();
      }
  });
  $("#buttonInput").click(function() {
    getBotResponse();
  })