var my_node_id;
var most_recent_question_number = 0;
var total_questions = 5;

// question relevant variables
var question_json, round, question_text, Wwer, Rwer, number, topic, round, pic, face1, face2, received_infos;

var get_info = function() {
  dallinger.getReceivedInfos(my_node_id)
    .done(function (resp) {
      received_infos = resp.infos;
      question_json = get_max_question(received_infos);
      if (typeof question_json != "undefined") {
          question_text = question_json.question;
          number = question_json.number;
          most_recent_question_number = number;
          round = question_json.round;
          if (round == 0) {
            pic = question_json.pic;
            Wwer = question_json.Wwer;
            Rwer = question_json.Rwer;
            topic = question_json.topic;
            display_question();  
          } else {
            face1 = question_json.face1;
            face2 = question_json.face2;
            display_faces();
          }
      } else {
        setTimeout(function() {
          get_info();
        }, 1000);
      }
    })
    .fail(function (rejection) {
      console.log(rejection);
      $('body').html(rejection.html);
    });
};

get_max_question = function(infos) {
  if (infos.length == 0) { return undefined; }

  newest_info = infos[0];
  for (i = 1; i < infos.length; i++) {
    if (infos[i].id > newest_info.id) {
      newest_info = infos[i];
    }
  }

  if (JSON.parse(newest_info.contents).number == most_recent_question_number) {
    return undefined;
  } else {
    return(JSON.parse(newest_info.contents));
  }
};

// display the question
display_question = function() {
    $("#question").html(question_text);
    $("#question_number").html("You are on question " + number + "/100");

    if (Math.random() < 0.5) {
      assign_button("a", Wwer);
      assign_button("b", Rwer);
    } else {
      assign_button("a", Rwer);
      assign_button("b", Wwer);
    }
    
    countdown = 15;
    $("#countdown").html(countdown);
    $("#question_div").show();
    $("#wait_div").hide();
    // start_answer_timeout();
};

// display the question
display_faces = function() {
    $("#question").html(question_text);
    $("#question_number").html("You are on question " + number + "/100");

    

    if (Math.random() < 0.5) {
      $("#face1").attr("src", face1);
      $("#face2").attr("src", face2);
    } else {
      $("#face1").attr("src", face2);
      $("#face2").attr("src", face1);
    }
    
    countdown = 15;
    $("#countdown").html(countdown);
    $("#question_div").show();
    $("#wait_div").hide();
    // start_answer_timeout();
};

assign_button = function(button, answer) {
  button_name = "#submit-" + button;
  $(button_name).html(answer);
  $(button_name).unbind('click');
  $(button_name).click(function() { submit_response(answer); });
};

hide_pics = function() {
    $("#pics").hide();
};

show_pics = function(number) {
    $("#pics").attr("src", "/static/images/" + number + ".png");
    $("#pics").show();
};

// Create the agent.
var create_agent = function() {
  $('#finish-reading').prop('disabled', true);
  dallinger.createAgent()
    .done(function (resp) {
      $('#finish-reading').prop('disabled', false);
      my_node_id = resp.node.id;
      store.set("my_node_id", my_node_id);
      get_info();
    })
    .fail(function (rejection) {
      // A 403 is our signal that it's time to go to the questionnaire
      if (rejection.status === 403) {
        dallinger.allowExit();
        dallinger.goToPage('questionnaire');
      } else {
        dallinger.error(rejection);
      }
    });
};

function recover_node_id() {
  my_node_id = store.get("my_node_id");
  get_info();
}

function submit_response(response) {
  $("#question_div").hide();
  $("#wait_div").show();
  dallinger.createInfo(my_node_id, {
    contents: response,
    details: JSON.stringify(question_json)
  }).done(function (resp) {
    if (number >= total_questions) {
      dallinger.goToPage('faces');
    } else {
      get_info();
    }
  })
  .fail(function (rejection) {
    dallinger.error(rejection);
  });
}
