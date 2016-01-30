/* JQuery deparam function

 https://github.com/chrissrogers/jquery-deparam/blob/master/jquery-deparam.min.js
 */
(function(h){h.deparam=function(i,j){var d={},k={"true":!0,"false":!1,"null":null};h.each(i.replace(/\+/g," ").split("&"),function(i,l){var m;var a=l.split("="),c=decodeURIComponent(a[0]),g=d,f=0,b=c.split("]["),e=b.length-1;/\[/.test(b[0])&&/\]$/.test(b[e])?(b[e]=b[e].replace(/\]$/,""),b=b.shift().split("[").concat(b),e=b.length-1):e=0;if(2===a.length)if(a=decodeURIComponent(a[1]),j&&(a=a&&!isNaN(a)?+a:"undefined"===a?void 0:void 0!==k[a]?k[a]:a),e)for(;f<=e;f++)c=""===b[f]?g.length:b[f],m=g[c]=f<e?g[c]||(b[f+1]&&isNaN(b[f+1])?{}:[]):a,g=m;else h.isArray(d[c])?d[c].push(a):d[c]=void 0!==d[c]?[d[c],a]:a;else c&&(d[c]=j?void 0:"")});return d}})(jQuery);


(function(){

    var template_prefix = 'template_';
    var div_prefix = 'div_template_';
    var cached = [];  // contains ints

    function load_template_handler(data, selected) {
        /* This function works with data from a JSON response, so it contains int
         values in places instead of strings.  Keep all usage everywhere else
         as strings and not ints to reduce type confusion. */
        var template_id = data['id'];
        var template_name = data['name'];
        var input_id = template_prefix + template_id.toString();

        // Create new form input.
        var input_div = $('<div/>', {
            class: 'form-group',
            id: div_prefix + template_id
        });
        var label = $('<label/>', {
            class: 'control-label',
            for: input_id
        });
        label.append(document.createTextNode(template_name));
        label.appendTo(input_div);
        var select = $('<select/>', {
            multiple: 'multiple',
            class: 'form-control',
            id: input_id,
            name: input_id,
            title: ''
        });
        select.appendTo(input_div);

        // Add field options.
        data['fields'].forEach(function(row){
            var id = row[0];
            var name = row[1];
            var option = $('<option/>', {
                value: id
            });

            // Select provided options.
            if ((typeof selected !== 'undefined') &&
                (selected.indexOf(id.toString()) !== -1)) {
                option.attr('selected', 'selected');
            }
            option.append(document.createTextNode(name));
            option.appendTo(select);
        });

        input_div.appendTo('#fields');

        // Sort field inputs.
        $('#fields').find('div').sort(function(a, b){
            var a_id = $(a).find('select').attr('id');
            var b_id = $(b).find('select').attr('id');
            return a_id.localeCompare(b_id);
        }).appendTo('#fields');

        cached.push(template_id);
    }

    /* Load template.

     Query for and add an input for the fields of the template.
     Optionally supply a list of fields to select.

     template_id is a string.
     */
    function load_template(template_id, selected) {
        // Some browsers don't support location.origin
        if (typeof location.origin === 'undefined') {
            location.origin = location.protocol + '//' + location.host;
        };

        $.get(location.origin +
              "{% url 'reports:template_fields' %}?id=" +
              template_id,
              function(data){ return load_template_handler(data, selected); });
    }

    function reload_template_fields() {
        /* On template selection change,

         We load selected templates.  For new templates, we query for the
         template's fields and make an input form.  If we already have an input
         form for it, we show it.

         */

        var selected = $('#id_templates').val();

        selected.forEach(function(template_id){
            if (cached.indexOf(parseInt(template_id)) === -1) {
                // Load new form.
                load_template(template_id);
            } else {
                // Unhide form.
                $('#' + template_prefix + template_id).attr(
                    'name', template_prefix + template_id);
                $('#' + div_prefix + template_id).show();
            }
        });

        // Hide unselected forms.
        cached.forEach(function(template_id){
            if (selected.indexOf(template_id.toString()) === -1) {
                $('#' + template_prefix + template_id).removeAttr('name');
                $('#' + div_prefix + template_id).hide();
            }
        });
    }

    $('#id_templates').change(function(e){
        reload_template_fields();
    });

    // Also on form reset.
    $('#report_form').on('reset', function(e){
        // Putting this in setTimeout makes sure it fires after the reset event.
        // At least depending on JS event stack implementation.
        setTimeout(function() {
            reload_template_fields();
        });
    });

    /* Generate template inputs for the templates in the GET request. */
    $(document).ready(function(){
        // location.search = '?param=value&param=value...'
        var params = location.search.slice(1);
        params = $.deparam(params);
        if (!('templates' in params)) {
            return;
        }
        var templates = params['templates'];
        if (typeof templates === 'string') {
            templates = [templates];
        }

        templates.forEach(function(template_id){
            var fields = params[template_prefix + template_id];
            if (typeof fields === 'string') {
                fields = [fields];
            }
            load_template(template_id, fields);
        });
    });

})();
