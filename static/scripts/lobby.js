var my_node_id, my_network_id, num_neighbors = -1;

$(document).ready(function() {
    get_node_id_or_create_agent();
    setTimeout(function() { initialize_alerts(); }, 3000);
    setTimeout(function() { $("#oops").show(); }, 1000*60*15);
    setTimeout(function() { go_to_questionnaire(); }, 1000*60*16);
});

function go_to_questionnaire() {
  dallinger.allowExit();
  dallinger.goToPage('survey');
}

function get_node_id_or_create_agent() {
    my_node_id = dallinger.storage.get("my_node_id");
    if (typeof my_node_id === "undefined") {
        create_agent();
    } else {
        my_network_id = dallinger.storage.get("my_network_id");
        check_to_advance_to_experiment();
    }
}

function initialize_alerts() {
    dallinger.storage.set("alert", true);
    dallinger.storage.set("mini_alert", false);
    $("#play-alert").click(function() { $('#alert').trigger('play'); }); 
    $("#play-mini-alert").click(function() { $('#dong').trigger('play'); });

    $("#toggle-alert").click(function() {
        var alert = dallinger.storage.get("alert");
        if (alert) {
            alert = dallinger.storage.set("alert", false);
            $("#toggle-alert").text("Enable alert");
            $("#alert-enabled").text("disabled");
        } else {
            alert = dallinger.storage.set("alert", true);
            $("#toggle-alert").text("Disable alert");
            $("#alert-enabled").text("enabled");
        }
    }); 

    $("#toggle-mini-alert").click(function() {
        var alert = dallinger.storage.get("mini_alert");
        if (alert) {
            alert = dallinger.storage.set("mini_alert", false);
            $("#toggle-mini-alert").text("Enable mini-alert");
            $("#mini-alert-enabled").text("disabled");
        } else {
            alert = dallinger.storage.set("mini_alert", true);
            $("#toggle-mini-alert").text("Disable mini-alert");
            $("#mini-alert-enabled").text("enabled");
        }
    });
}

function create_agent() {
  dallinger.createAgent()
    .done(function (resp) {
        my_node = resp.node;
        my_node_id = resp.node.id;
        store.set("my_node_id", my_node_id);
        my_network_id = resp.node.network_id;
        dallinger.storage.set("my_network_id", my_network_id);
        check_to_advance_to_experiment();
    })
    .fail(function (rejection) { go_to_questionnaire(); });
}

function check_to_advance_to_experiment() {
    dallinger.getReceivedInfos(my_node_id)
    .done(function(resp) {
        if (resp.infos.length > 0) {
            dallinger.allowExit();
            dallinger.goToPage("experiment");
        } else {
            update_ui_and_try_again();
        }
    })
    .fail(function (rejection) { go_to_questionnaire(); });
}

function update_ui_and_try_again() {
    update_max_group_size();
    update_current_group_size();
    setTimeout(function() { check_to_advance_to_experiment(); }, 1500);
}

function update_max_group_size() {
    dallinger.getExperimentProperty('ppts_per_network')
    .done(function (resp) {
        $('#max-group-size').text(resp.ppts_per_network);
    })
    .fail(function (rejection) { go_to_questionnaire(); });
}

update_current_group_size = function() {
    dallinger.get(
        "/node/" + my_node_id + "/neighbors",
        { connection: "to" }
    ).done(function (resp) {
        neighbors = resp.nodes;

        new_num_neighbors = neighbors.length;
        if (new_num_neighbors !== num_neighbors & num_neighbors !== -1 & dallinger.storage.get("mini_alert")) {
            $('#dong').trigger('play');
        }
        num_neighbors = new_num_neighbors;
        $('#current-group-size').text(num_neighbors + 1);

        all_nodes = [].concat(neighbors);
        all_nodes.push(my_node);
        oldest_node = all_nodes[0];
        if (all_nodes.length > 1) {
            for (i = 1; i < all_nodes.length; i++) {
                if (all_nodes[i].id < oldest_node.id) {
                    oldest_node = all_nodes[i];
                }
            }
        }

        start_time = oldest_node.creation_time;
        now = new Date();
        milliseconds = ((new Date(now)) - (new Date(start_time)));
        minutes = milliseconds / (60000);
        minutes_left = Math.round(15 - minutes);
        $('#minutes-left').text(minutes_left);
    })
    .fail(function (rejection) { go_to_questionnaire(); });
};
