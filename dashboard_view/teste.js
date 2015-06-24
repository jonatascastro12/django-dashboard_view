jQuery(function ($) {

    window.django_select2.id_userprofiles = function (selector, fieldID) {
        var hashedSelector = "#" + selector;
        $(hashedSelector).data("field_id", fieldID);

        window.django_select2.id_userprofiles = function (selector, fieldID) {
            var hashedSelector = "#" + selector;
            $(hashedSelector).data("field_id", fieldID);
            $(hashedSelector).change(django_select2.onValChange).data("userGetValText", null);
            $("#id_userprofiles").txt(["Eli Vilela", "Felipe Ferreira Neves"]);
            var hashedSelector = "#" + "id_userprofiles";
            $(hashedSelector).select2({"initSelection": django_select2.onInit,
                "ajax": {
                    "dataType": "json",
                    "quietMillis": 100,
                    "url": "/select2/fields/auto.json",
                    "data": django_select2.runInContextHelper(django_select2.get_url_params, selector),
                    "results": django_select2.runInContextHelper(django_select2.process_results, selector)
                },
                "multiple": true,
                "minimumInputLength": 2,
                "separator": django_select2.MULTISEPARATOR,
                "closeOnSelect": false,
                "placeholder": ""
            });
        };
        django_select2.id_userprofiles("id_userprofiles", "0202f80adb1162c7b6071fd7fe5055a5781ea5db");
    };
    django_select2.id_userprofiles("id_userprofiles", "0202f80adb1162c7b6071fd7fe5055a5781ea5db");
});
                