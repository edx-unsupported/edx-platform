

(function(globals) {

  var django = globals.django || (globals.django = {});


  django.pluralidx = function(n) {
    var v=(n != 1);
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };


  /* gettext library */

  django.catalog = django.catalog || {};

  var newcatalog = {
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s of %(cnt)s selected",
      "%(sel)s of %(cnt)s selected"
    ],
    "6 a.m.": "\u0b95\u0bbe\u0bb2\u0bc8 6 \u0bae\u0ba3\u0bbf  ",
    "Available %s": "%s \u0b87\u0bb0\u0bc1\u0b95\u0bcd\u0b95\u0bbf\u0bb1\u0ba4\u0bbe ",
    "Cancel": "\u0bb5\u0bc7\u0ba3\u0bcd\u0b9f\u0bbe\u0bae\u0bcd ",
    "Choose": "Choose",
    "Choose a time": "\u0b92\u0bb0\u0bc1 \u0ba8\u0bc7\u0bb0\u0ba4\u0bcd\u0ba4\u0bc8 \u0ba4\u0bc7\u0bb0\u0bcd\u0ba8\u0bcd\u0ba4\u0bcd\u0ba4\u0bc6\u0b9f\u0bc1\u0b95\u0bcd\u0b95  ",
    "Choose all": "\u0b8e\u0bb2\u0bcd\u0bb2\u0bbe\u0bb5\u0bb1\u0bcd\u0bb1\u0bc8\u0baf\u0bc1\u0bae\u0bcd \u0ba4\u0bc7\u0bb0\u0bcd\u0ba8\u0bcd\u0ba4\u0bcd\u0ba4\u0bc6\u0b9f\u0bc1\u0b95\u0bcd\u0b95",
    "Chosen %s": "%s \u0ba4\u0bc7\u0bb0\u0bcd\u0ba8\u0bcd\u0ba4\u0bcd\u0ba4\u0bc6\u0b9f\u0bc1\u0b95\u0bcd\u0b95\u0baa\u0bcd\u0baa\u0b9f\u0bcd\u0b9f",
    "Click to choose all %s at once.": "Click to choose all %s at once.",
    "Click to remove all chosen %s at once.": "Click to remove all chosen %s at once.",
    "Filter": "\u0bb5\u0b9f\u0bbf\u0b95\u0b9f\u0bcd\u0b9f\u0bbf",
    "Hide": "Hide",
    "Midnight": "\u0ba8\u0b9f\u0bc1 \u0b87\u0bb0\u0bb5\u0bc1 ",
    "Noon": "\u0bae\u0ba4\u0bbf\u0baf\u0bae\u0bcd ",
    "Now": "\u0b87\u0baa\u0bcd\u0baa\u0bc6\u0bbe\u0bb4\u0bc1\u0ba4\u0bc1 ",
    "Remove": "\u0b85\u0bb4\u0bbf\u0b95\u0bcd\u0b95",
    "Remove all": "Remove all",
    "Show": "Show",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.",
    "Today": "\u0b87\u0ba9\u0bcd\u0bb1\u0bc1 ",
    "Tomorrow": "\u0ba8\u0bbe\u0bb3\u0bc8",
    "Type into this box to filter down the list of available %s.": "Type into this box to filter down the list of available %s.",
    "Yesterday": "\u0ba8\u0bc7\u0bb1\u0bcd\u0bb1\u0bc1 ",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost."
  };
  for (var key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }


  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      var value = django.catalog[msgid];
      if (typeof(value) == 'undefined') {
        return msgid;
      } else {
        return (typeof(value) == 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      var value = django.catalog[singular];
      if (typeof(value) == 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value.constructor === Array ? value[django.pluralidx(count)] : value;
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      var value = django.gettext(context + '\x04' + msgid);
      if (value.indexOf('\x04') != -1) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      var value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.indexOf('\x04') != -1) {
        value = django.ngettext(singular, plural, count);
      }
      return value;
    };

    django.interpolate = function(fmt, obj, named) {
      if (named) {
        return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
      } else {
        return fmt.replace(/%s/g, function(match){return String(obj.shift())});
      }
    };


    /* formatting library */

    django.formats = {
    "DATETIME_FORMAT": "N j, Y, P",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d",
      "%m/%d/%Y %H:%M:%S",
      "%m/%d/%Y %H:%M:%S.%f",
      "%m/%d/%Y %H:%M",
      "%m/%d/%Y",
      "%m/%d/%y %H:%M:%S",
      "%m/%d/%y %H:%M:%S.%f",
      "%m/%d/%y %H:%M",
      "%m/%d/%y"
    ],
    "DATE_FORMAT": "j F, Y",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%m/%d/%Y",
      "%m/%d/%y",
      "%b %d %Y",
      "%b %d, %Y",
      "%d %b %Y",
      "%d %b, %Y",
      "%B %d %Y",
      "%B %d, %Y",
      "%d %B %Y",
      "%d %B, %Y"
    ],
    "DECIMAL_SEPARATOR": ".",
    "FIRST_DAY_OF_WEEK": 0,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 0,
    "SHORT_DATETIME_FORMAT": "m/d/Y P",
    "SHORT_DATE_FORMAT": "j M, Y",
    "THOUSAND_SEPARATOR": ",",
    "TIME_FORMAT": "g:i A",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
  };

    django.get_format = function(format_type) {
      var value = django.formats[format_type];
      if (typeof(value) == 'undefined') {
        return format_type;
      } else {
        return value;
      }
    };

    /* add to global namespace */
    globals.pluralidx = django.pluralidx;
    globals.gettext = django.gettext;
    globals.ngettext = django.ngettext;
    globals.gettext_noop = django.gettext_noop;
    globals.pgettext = django.pgettext;
    globals.npgettext = django.npgettext;
    globals.interpolate = django.interpolate;
    globals.get_format = django.get_format;

    django.jsi18n_initialized = true;
  }

}(this));

