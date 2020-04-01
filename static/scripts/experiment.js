var my_node_id;
var most_recent_question_number = 0;

var get_info = function() {
  // Get info for node
  dallinger.getReceivedInfos(my_node_id)
    .done(function (resp) {
      var question_json = get_max_question(resp.infos);
      if (typeof question_json != "undefined") {
          round = question_json.round;
          question_text = question_json.question;
          Wwer = question_json.Wwer;
          Rwer = question_json.Rwer;
          number = question_json.number;
          most_recent_question_number = number;
          topic = question_json.topic;
          round = question_json.round;
          pic = question_json.pic;
          display_question();
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
  var current_max_question;
  for (i = 0; i < infos.length; i++) {
    this_info = JSON.parse(infos[i].contents);
    if (this_info.number > most_recent_question_number) {
      most_recent_question_number = this_info.number;
      current_max_question = this_info;
    }
  }
  return(current_max_question);
};

// display the question
display_question = function() {
    $("#question").html(question_text);
    $("#question_number").html("You are on question " + number + "/100");
    
    if (pic == true) {
        show_pics(number);
    } else {
        hide_pics();
    }

    if (Math.random() < 0.5) {
        $("#submit-a").html(Wwer);
        $("#submit-b").html(Rwer);
    } else {
        $("#submit-b").html(Wwer);
        $("#submit-a").html(Rwer);
    }
    
    countdown = 15;
    $("#countdown").html(countdown);
    $("#question_div").show();
    $("#wait_div").hide();
    // start_answer_timeout();
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

// Consent to the experiment.
$(document).ready(function() {

  $("#submit-a").click(function() {
    submit_response(get_button_text("#submit-a"));
  });

  $("#submit-b").click(function() {
    submit_response(get_button_text("#submit-b"));
  });
});

function get_button_text(button) {
  return($(button).text());
}

function submit_response(response) {
  $("#question_div").hide();
  $("#wait_div").show();
  dallinger.createInfo(my_node_id, {
    contents: response
  }).done(function (resp) {
    get_info();
  })
  .fail(function (rejection) {
    dallinger.error(rejection);
  });
}
