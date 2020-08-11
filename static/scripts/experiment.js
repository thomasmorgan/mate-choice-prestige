var my_node_id;
var most_recent_question_number = 0;
var most_recent_info_id = 0;
var total_questions = 5;
var total_faces = 5;

// question relevant variables
var newest_info, question_json, round, question_text, wrong_answer, right_answer, number, round, face1, face2, faces_inverted, received_infos;

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
          question_json = JSON.parse(newest_info.contents);
          question_text = question_json.question;
          number = question_json.number;
          most_recent_question_number = number;
          round = question_json.round;
          face1 = question_json.face1;
          face2 = question_json.face2;
          display_faces();
        } else if (newest_info.type == "summary") {
          question_json = JSON.parse(newest_info.contents);
          face1_string = "";
          face2_string = "";

          for (i=0;i<question_json.length;i++) {
            node_summary = question_json[i];
            summary_string = "Participant " + node_summary.id_within_group + " chose this face. Their pretest score is " + node_summary.score + ".<br>";
            if (node_summary.id == my_node_id) {
              summary_string = "";
            }
            if (node_summary.face == face1) {
              face1_string += summary_string;
            } else {
              face2_string += summary_string;
            }
          }

          if (faces_inverted) {
            $("#summary2").html(face1_string);
            $("#summary1").html(face2_string);
            $("#face1").click(function() { submit_final_response(face2); });
            $("#face2").click(function() { submit_final_response(face1); });
          } else {
            $("#summary1").html(face1_string);
            $("#summary2").html(face2_string);
            $("#face1").click(function() { submit_final_response(face1); });
            $("#face2").click(function() { submit_final_response(face2); });
          }
          $("#question_div").show();
          $("#face_row").show();
          $("#summary_row").show();
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

    if (Math.random() < 0.5) {
      faces_inverted = false;
      $("#face1").attr("src", face1);
      $("#face2").attr("src", face2);
      $("#face1").click(function() { submit_response(face1); });
      $("#face2").click(function() { submit_response(face2); });
    } else {
      faces_inverted = true;
      $("#face1").attr("src", face2);
      $("#face2").attr("src", face1);
      $("#face1").click(function() { submit_response(face2); });
      $("#face2").click(function() { submit_response(face1); });
    }
    
    $("#question_div").show();
    $("#face_row").show();
    $("#wait_div").hide();
    // start_answer_timeout();
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
  most_recent_question_number = store.get("most_recent_question_number");
  most_recent_info_id = store.get("most_recent_info_id");
  get_info();
}

function submit_response(response) {
  $("#question_div").hide();
  $("#wait_div").show();
  $("#face1").unbind('click');
  $("#face2").unbind('click');
  var types = ["QuizAnswer", "FaceAnswer1"];
  dallinger.createInfo(my_node_id, {
    contents: response,
    info_type: types[round],
    details: JSON.stringify(question_json)
  }).done(function (resp) {
    store.set("most_recent_question_number", most_recent_question_number);
    store.set("most_recent_info_id", most_recent_info_id);
    if (number >= total_questions & round == 0) {
      dallinger.goToPage('faces');
    } else {
      get_info();
    }
  })
  .fail(function (rejection) {
    dallinger.error(rejection);
  });
}

function submit_final_response(response) {
  $("#question_div").hide();
  $("#wait_div").show();
  $("#summary_row").hide();
  $("#face1").unbind('click');
  $("#face2").unbind('click');
  dallinger.createInfo(my_node_id, {
    contents: response,
    info_type: "FaceAnswer2",
    details: JSON.stringify(question_json)
  }).done(function (resp) {
    store.set("most_recent_question_number", most_recent_question_number);
    store.set("most_recent_info_id", most_recent_info_id);
    if (number >= total_questions & round == 0) {
      dallinger.goToPage('faces');
    } else if (number >= total_faces & round == 1) {
      dallinger.goToPage('survey');
    } else {
      get_info();
    }
  })
  .fail(function (rejection) {
    dallinger.error(rejection);
  });
}

var age = document.getElementById("age");

//Create array of options to be added
var array = ["18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", 
  "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", 
  "56", "57", "58", "59", "60", "61", "62", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", 
  "76", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", 
  "96", "97", "98", "99", "100"];

//Create and append select list
var selectList = document.createElement("select");
selectList.setAttribute("age", "mySelect");
myDiv.appendChild(selectList);

//Create and append the options
for (var i = 0; i < array.length; i++) {
    var option = document.createElement("option");
    option.setAttribute("value", array[i]);
    option.text = array[i];
    selectList.appendChild(option);
}

