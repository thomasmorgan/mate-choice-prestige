var my_node_id;
var most_recent_question_number = 0;
var most_recent_info_id = 0;
var total_questions = 5;

// question relevant variables
var newest_info, question_json, round, question_text, wrong_answer, right_answer, number, round, face1, face2, received_infos;

var get_info = function() {
  dallinger.getReceivedInfos(my_node_id)
    .done(function (resp) {
      received_infos = resp.infos;
      newest_info = get_max_question(received_infos);
      if (typeof newest_info != "undefined") {
        if (newest_info.type == "info") {
          question_json = JSON.parse(newest_info.contents);
          question_text = question_json.question;
          number = question_json.number;
          most_recent_question_number = number;
          round = question_json.round;
          wrong_answer = question_json.wrong_answer;
          right_answer = question_json.right_answer;
          display_question();  
        } else if (newest_info.type == "face_pairs") {
          // do stuff here.
          question_json = JSON.parse(newest_info.contents);
          question_text = question_json.question;
          number = question_json.number;
          most_recent_question_number = number;
          round = question_json.round;
          face1 = question_json.face1;
          face2 = question_json.face2;
          display_faces();
        } else if (newest_info.type == "summary") {
          // do more stuff
          // put the various bits of info into the table, etc
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

  // if (JSON.parse(newest_info.contents).number == most_recent_question_number) {
  if (newest_info.id == most_recent_info_id) {
    return undefined;
  } else {
    //return(JSON.parse(newest_info.contents));
    most_recent_info_id = newest_info.id;
    return newest_info;
  }
};

// display the question
display_question = function() {
    $("#question").html(question_text);
    $("#question_number").html("You are on question " + number + " of 30");

    if (Math.random() < 0.5) {
      assign_button("a", wrong_answer);
      assign_button("b", right_answer);
    } else {
      assign_button("a", right_answer);
      assign_button("b", wrong_answer);
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

display_faces = function() {
    $("#question").html(question_text);
    $("#question_number").html("You are on face " + number + " of 30");

    $("#face1").unbind('click');
    $("#face2").unbind('click');
    if (Math.random() < 0.5) {
      $("#face1").attr("src", face1);
      $("#face2").attr("src", face2);
      $("#face1").click(function() { submit_response(face1); });
      $("#face2").click(function() { submit_response(face2); });
    } else {
      $("#face1").attr("src", face2);
      $("#face2").attr("src", face1);
      $("#face1").click(function() { submit_response(face2); });
      $("#face2").click(function() { submit_response(face1); });
    }
    
    countdown = 15;
    $("#countdown").html(countdown);
    $("#question_div").show();
    $("#wait_div").hide();
    // start_answer_timeout();
};

//assign_face = function(button, answer) {
  //face_button = "#submit-" + face;
  //$(face_button).html(answer);
  //$(face_button).unbind('click');
  //$(face_button).click(function() { submit_response(answer); });
//};

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
  most_recent_question_number = store.get("most_recent_question_number");
  most_recent_info_id = store.get("most_recent_info_id");
  get_info();
}

function submit_response(response) {
  $("#question_div").hide();
  $("#wait_div").show();
  var types = ["QuizAnswer", "FaceAnswer1"];
  dallinger.createInfo(my_node_id, {
    contents: response,
    info_type: types[round],
    details: JSON.stringify(question_json)
  }).done(function (resp) {
    store.set("most_recent_question_number", most_recent_question_number);
    store.set("most_recent_info_id", most_recent_info_id);
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
