var my_node_id;

var get_info = function() {
  // Get info for node
  dallinger.getReceivedInfos(my_node_id)
    .done(function (resp) {
      num_infos = resp.infos.length;
      if (num_infos > 0) {
        var question_json = JSON.parse(resp.infos[0].contents);
        round = question_json.round;
        question_text = question_json.question;
        Wwer = question_json.Wwer;
        Rwer = question_json.Rwer;
        number = question_json.number;
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
  dallinger.createInfo(my_node_id, {
    contents: response
  }).done(function (resp) {
    get_info();
  })
  .fail(function (rejection) {
    dallinger.error(rejection);
  });
}
