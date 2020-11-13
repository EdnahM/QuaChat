const popup = document.querySelector('.chat-popup');
const chatBtn = document.querySelector('.chat-btn');
const submitBtn = document.querySelector('.submit');
const chatArea = document.querySelector('.chat-area');
const inputElm = document.querySelector('input')

const emojiBtn = document.querySelector('#emoji-btn');
const picker = new EmojiButton();

// Emoji Selection bit
emojiBtn.addEventListener('click', () => {
  picker.togglePicker(emojiBtn);
});

picker.on('emoji', emoji => {
   document.querySelector('#input').value += emoji;
});

// Chat Button Toggler
chatBtn.addEventListener('click', ()=>{
  popup.classList.toggle('show');
});

function getBotResponse() {
  let userInput = inputElm.value;
  $.get("/get", { msg: userInput }).done(function(data) {
    let response = `
    <div class="income-msg">
        <img src="static/img/pic.png" alt="" class="avatar">
        <span class="msg">` + data + `</span>
    `
    chatArea.insertAdjacentHTML("beforeend", response);

  });
  
  let temp = `<div class="out-msg">
  <span class="my-msg">${userInput}</span>
  <img src="static/img/image.png" class="avatar">
  </div>`

  chatArea.insertAdjacentHTML("beforeend", temp);
  inputElm.value = '';
}

// send msg
submitBtn.addEventListener('click', getBotResponse);

$("#input").keypress(function(e) {
  //if enter key is pressed
      if(e.which == 13) {
          getBotResponse();
      }
  });

//  function getBotResponse() {
//   var rawText = $("#input").val();
//   var userHtml = `<div class="out-msg">
//   <span class="my-msg">${userInput}</span>
//   <img src="static/img/pic.png" class="avatar">
//   </div>`
  
//   $("#input").val("");
//   $("#chat-area").append(userHtml);
//   document.getElementById('userInput').scrollIntoView({block: 'start', behavior: 'smooth'});
//   $.get("/get", { msg: rawText }).done(function(data) {
//     var botHtml = '<p class="botText"><img class=" img-circle avatar" style="width:10%;" src="./static/icon2.jpg" /><span>' + data + '</span></p>';
//     $("#chatbox").append(botHtml);
//     document.getElementById('userInput').scrollIntoView({block: 'start', behavior: 'smooth'});
//   });
// }
// $("#textInput").keypress(function(e) {
//     if(e.which == 13) {
//         getBotResponse();
//     }
// });
// $("#buttonInput").click(function() {
//   getBotResponse();
// })