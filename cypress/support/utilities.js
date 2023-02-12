module.exports.random_string = random_string
module.exports.create_minimum_event_object = create_minimum_event_object
module.exports.get_event_kind = get_event_kind

const EventKinds = {
    ONE_DAY: "Jednodenní akce",
    WEEKEND: "Víkendovka",
    CAMP: "Tábor"
}

function get_event_kind(kind) {
    let result = EventKinds[kind]
    if (typeof (result) == "undefined") {
        throw new Error("Unknown event kind \"$kind\"")
    }
    return result
}


function random_string(length) {
    let result = '';
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
        result += characters.charAt(Math.floor(Math.random() * charactersLength));
        counter += 1;
    }
    return result;
}

function create_minimum_event_object(kind, start_date, end_date, count = 1, for_first_time_participant = false, name = null) {
    if (name === null) {
        name = random_string(10)
    }
    let kind_enum = get_event_kind(kind)

    return {
        "name": name,
        "kind": kind_enum,
        "start_date": start_date,
        "end_date": end_date,
        "count": count,
        "for_first_time_participant": for_first_time_participant,
        "show_on_web": false,
        "location": "online"
    }
}
