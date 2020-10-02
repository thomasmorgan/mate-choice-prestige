var my_node_id, received_infos, newest_info, number, round, question_json, question_text, right_answer, wrong_answer, face1, face2, faces_inverted, face1_summary, face2_summary;

var most_recent_question_number = 0;
var most_recent_info_id = 0;

var total_questions = 30;
var total_faces = 30;

function go_to_questionnaire() {
  dallinger.allowExit();
  dallinger.goToPage('survey');
}

function get_info() {
  dallinger.getReceivedInfos(my_node_id)
    .done(function (resp) {
      received_infos = resp.infos;
      if (received_new_info()) {
        identify_new_info();
        if (newest_info.type == "info") {
          read_question();
          display_question();  
        } else if (newest_info.type == "face_pairs") {
          read_face_pair();
          display_faces();
        } else if (newest_info.type == "summary") {
          create_summary();
          display_summary();
        }
      } else {
        setTimeout(function() {
          get_info();
        }, 1000);
      }
    })
    .fail(function (rejection) { go_to_questionnaire(); });
}

function received_new_info() {
  if (received_infos.length == 0) { return false; }
  else { return(max_received_info_id() > most_recent_info_id); }
}

function max_received_info_id() {
  var max_id = 0;
  for (i = 0; i < received_infos.length; i++) {
    if (received_infos[i].id > max_id) {
      max_id = received_infos[i].id;
    }
  }
  return max_id;
}

function identify_new_info() {
  received_infos.forEach(function(this_info) {
    if (this_info.id == max_received_info_id()) {
      newest_info = this_info;
      most_recent_info_id = this_info.id;
    }
  });
}

function read_question() {
  question_json = JSON.parse(newest_info.contents);
  question_text = question_json.question;
  number = question_json.number;
  most_recent_question_number = number;
  round = question_json.round;
  wrong_answer = question_json.wrong_answer;
  right_answer = question_json.right_answer;
}

function display_question() {
    $("#question").html(question_text);
    $("#question_number").html("You are on question " + number + " of 30");

    if (Math.random() < 0.5) {
      assign_button("a", wrong_answer);
      assign_button("b", right_answer);
    } else {
      assign_button("a", right_answer);
      assign_button("b", wrong_answer);
    }
    
    $("#wait_div").hide();
    $("#pretest_wait_div").hide();
    $("#question_div").show();
};

function assign_button(button, answer) {
  var button_name = "#submit-" + button;
  $(button_name).html(answer);
  $(button_name).unbind('click');
  $(button_name).click(function() { submit_response(answer, "QuizAnswer"); });
};

function read_face_pair() {
  question_json = JSON.parse(newest_info.contents);
  question_text = question_json.question;
  number = question_json.number;
  most_recent_question_number = number;
  round = question_json.round;
  face1 = question_json.face1;
  face2 = question_json.face2;
}

function display_faces() {
  $("#question").html(question_text);
  $("#question_number").html("You are on face pair " + number + " of 30");

  $("#face1").unbind('click');
  $("#face2").unbind('click');

  if (Math.random() < 0.5) {
    faces_inverted = false;
    $("#face1").attr("src", face1);
    $("#face2").attr("src", face2);
    $("#face1").click(function() { submit_response(face1, "FaceAnswer1"); });
    $("#face2").click(function() { submit_response(face2, "FaceAnswer1"); });
  } else {
    faces_inverted = true;
    $("#face1").attr("src", face2);
    $("#face2").attr("src", face1);
    $("#face1").click(function() { submit_response(face2, "FaceAnswer1"); });
    $("#face2").click(function() { submit_response(face1, "FaceAnswer1"); });
  }
  
  $("#wait_div").hide();
  $("#pretest_wait_div").hide();
  $("#summary_row").hide();
  $("#face_row").show();
  $("#question_div").show();
}

function create_summary() {
  question_json = JSON.parse(newest_info.contents);
  face1_summary = "";
  face2_summary = "";

  for (i=0;i<question_json.length;i++) {
    node_summary = question_json[i];
    if (node_summary.id != my_node_id) {
      node_summary = question_json[i];
      summary_string = "Participant " + node_summary.id_within_group + " chose this person. Their quiz score is " + node_summary.score + ".<br>";
      if (node_summary.face == face1) { face1_summary += summary_string; }
      else { face2_summary += summary_string; }
    }
  }
}

function display_summary() {
  $("#face1").unbind('click');
  $("#face2").unbind('click');

  if (faces_inverted) {
    $("#summary2").html(face1_summary);
    $("#summary1").html(face2_summary);
    $("#face1").click(function() { submit_response(face2, "FaceAnswer2"); });
    $("#face2").click(function() { submit_response(face1, "FaceAnswer2"); });
  } else {
    $("#summary1").html(face1_summary);
    $("#summary2").html(face2_summary);
    $("#face1").click(function() { submit_response(face1, "FaceAnswer2"); });
    $("#face2").click(function() { submit_response(face2, "FaceAnswer2"); });
  }

  $("#question").html("Please review the decisions of your group mates and make a final decision.");

  $("#question_div").show();
  $("#face_row").show();
  $("#summary_row").show();
  $("#wait_div").hide();
  $("#pretest_wait_div").hide();
}

function recover_node_id() {
  my_node_id = store.get("my_node_id");
}

function recover_stored_variables() {
  recover_node_id();
  most_recent_question_number = store.get("most_recent_question_number");
  most_recent_info_id = store.get("most_recent_info_id");
}

function submit_response(response, type) {
  $("#question_div").hide();
  $("#wait_div").show();
  dallinger.createInfo(my_node_id, {
    contents: response,
    info_type: type,
    details: JSON.stringify(question_json)
  }).done(function(resp) {
    store.set("most_recent_question_number", most_recent_question_number);
    store.set("most_recent_info_id", most_recent_info_id);
    advance_to_next_question(type);
  }).fail(function (rejection) {
    go_to_questionnaire();
  });
}

function advance_to_next_question(type) {
  if (type == "QuizAnswer") {
    if (number >= total_questions) { dallinger.goToPage('faces'); }
    else { get_info(); }
  } else if (type == "FaceAnswer1") {
    get_info();
  } else {
    if (number >= total_faces) { dallinger.goToPage('survey'); }
    else { get_info(); }
  }
}

$(document).ready(function() {
  if ($('#age').length) {
    for (i=18; i<101; i++) {
      $("#age").append('<option value="' + i + '">' + i + '</option>');
    }
  }
});
