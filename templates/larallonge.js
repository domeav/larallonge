const contributions = {{ contributions|safe }};

const children = {{ children|safe }};

function make_key(node_type, id){
    return node_type + '_' + id.padStart(4, '0');
}

function credits(participations){
    var people = [];
    participations.forEach(p => {
        var cred = p['person'];
        if ('details' in p){
            cred = cred + ' (' + p['details'] + ')';
        }
        people.push(cred);
    });
    return people.join(', ');
}
