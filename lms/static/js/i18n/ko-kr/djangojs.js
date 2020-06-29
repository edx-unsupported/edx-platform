

(function(globals) {

  var django = globals.django || (globals.django = {});


  django.pluralidx = function(n) {
    var v=0;
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };


  /* gettext library */

  django.catalog = django.catalog || {};

  var newcatalog = {
    " menu to see a list of all topics.": " \uba54\ub274\ub97c \uc0ac\uc6a9\ud558\uc5ec \ubaa8\ub4e0 \uc8fc\uc81c\uc758 \ubaa9\ub85d\uc744 \ubcfc \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "%(comments_count)s %(span_sr_open)scomments %(span_close)s": "%(comments_count)s\uac1c %(span_sr_open)s\ub313\uae00 %(span_close)s",
    "%(comments_count)s %(span_sr_open)scomments (%(unread_comments_count)s unread comments)%(span_close)s": "%(comments_count)s\uac1c %(span_sr_open)s\ub313\uae00(%(unread_comments_count)s\uac1c \uc77d\uc9c0 \uc54a\uc740 \ub313\uae00)%(span_close)s",
    "%(num_questions)s question": [
      "%(num_questions)s\uac1c"
    ],
    "%(num_students)s student": [
      " %(num_students)s \uba85 "
    ],
    "%(num_students)s student opened Subsection": [
      "\uc18c\uc8fc\uc81c\ub97c \uc5f4\uc5b4\ubcf8 \ud559\uc2b5\uc790\ub4e4 : %(num_students)s"
    ],
    "%(post_type)s posted %(time_ago)s by %(author)s": "%(time_ago)s\uc5d0 %(author)s\uc774(\uac00) \uac8c\uc2dc\ud55c %(post_type)s",
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s\uac1c\uac00 %(cnt)s\uac1c \uc911\uc5d0 \uc120\ud0dd\ub428."
    ],
    "%(team_count)s Team": [
      "%(team_count)s \ud300"
    ],
    "6 a.m.": "\uc624\uc804 6\uc2dc",
    "6 p.m.": "\uc624\ud6c4 6\uc2dc",
    "Account Settings": "\uacc4\uc815 \uc124\uc815",
    "(Community TA)": "(\ucee4\ubba4\ub2c8\ud2f0 \uc870\uad50)",
    "(Staff)": "(\uc9c1\uc6d0)",
    "(this post is about %(courseware_title_linked)s)": "(%(courseware_title_linked)s\uc5d0 \ub300\ud55c \uac8c\uc2dc\uae00)",
    "Add Cohort": "\ud559\uc2b5\uc9d1\ub2e8 \ucd94\uac00\ud558\uae30",
    "Add a New Cohort": "\uc2e0\uaddc \ud559\uc2b5 \uc9d1\ub2e8 \ucd94\uac00",
    "Add a Post": "\uac8c\uc2dc\uae00 \ucd94\uac00",
    "Add a Response": "\uc751\ub2f5 \ucd94\uac00",
    "Add a clear and descriptive title to encourage participation. (Required)": "\ucc38\uc5ec\ub97c \ub3c5\ub824\ud558\ub294 \ubd84\uba85\ud558\uace0 \uad6c\uccb4\uc801\uc778 \uc81c\ubaa9\uc744 \ucd94\uac00\ud558\uc2ed\uc2dc\uc624(\ud544\uc218).",
    "Add a comment": "\ub313\uae00 \ucd94\uac00",
    "Add a response:": "\uc751\ub2f5 \ucd94\uac00:",
    "Add your post to a relevant topic to help others find it. (Required)": "\ub2e4\ub978 \uc218\uac15\uc790\uac00 \ucc3e\uc744 \uc218 \uc788\ub3c4\ub85d \uad00\ub828 \uc8fc\uc81c\uc5d0 \uac8c\uc2dc\uae00\uc744 \ucd94\uac00\ud558\uc2ed\uc2dc\uc624(\ud544\uc218).",
    "Adding the selected course to your cart": "\uc7a5\ubc14\uad6c\ub2c8\uc5d0 \uc120\ud0dd\ub41c \uac15\uc88c\ub97c \ucd94\uac00\ud558\uace0 \uc788\uc2b5\ub2c8\ub2e4.",
    "Additional posts could not be loaded. Refresh the page and try again.": "\ucd94\uac00 \uac8c\uc2dc\uae00\uc744 \ub85c\ub4dc\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "Additional responses could not be loaded. Refresh the page and try again.": "\ucd94\uac00 \uc751\ub2f5\uc744 \ub85c\ub4dc\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "All Groups": "\ubaa8\ub4e0 \uadf8\ub8f9",
    "All Posts": "\ubaa8\ub4e0 \uac8c\uc2dc\uae00",
    "All Topics": "\ubaa8\ub4e0 \uc8fc\uc81c",
    "All accounts were created successfully.": "\ubaa8\ub4e0 \uacc4\uc815\uc774 \uc0dd\uc131\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "All subsections": "\ubaa8\ub4e0 \uc18c\uc8fc\uc81c",
    "All units": "\uc804\uccb4 \ud559\uc2b5\ud65c\ub3d9",
    "Allow students to generate certificates for this course?": "\ud559\uc2b5\uc790\uc758 \uc774\uc218\uc99d \uc0dd\uc131\uc744 \ud5c8\uc6a9\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?",
    "An error has occurred. Make sure that you are connected to the Internet, and then try refreshing the page.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \uc778\ud130\ub137\uc5d0 \uc5f0\uacb0\ub418\uc5b4 \uc788\ub294\uc9c0 \ud655\uc778\ud55c \ud6c4, \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68 \ud558\uc138\uc694.",
    "An error has occurred. Please try again later.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.",
    "An error has occurred. Please try again.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.",
    "An error has occurred. Please try reloading the page.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \ub2e4\uc2dc \ubd88\ub7ec\uc624\uc138\uc694.",
    "An error has occurred. Refresh the page, and then try again.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ud6c4, \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694. ",
    "An error occurred retrieving your email. Please try again later, and contact technical support if the problem persists.": "\uc774\uba54\uc77c\uc744 \uac80\uc0c9\ud558\ub294 \ub3d9\uc548 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub098\uc911\uc5d0 \ub2e4\uc2dc \uc2dc\ub3c4\ud55c \ud6c4, \ubb38\uc81c\uac00 \uc9c0\uc18d\ub418\uba74 \uae30\uc220 \uc9c0\uc6d0\ud300\uc5d0 \uc5f0\ub77d\uc8fc\uc138\uc694.",
    "An error occurred. Make sure that the student's username or email address is correct and try again.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ud559\uc2b5\uc790\uc758 \uc544\uc774\ub514\uc640 \uc774\uba54\uc77c \uc8fc\uc18c\uac00 \uc62c\ubc14\ub978\uc9c0 \ud655\uc778\ud558\uace0 \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \uc8fc\uc138\uc694.",
    "An error occurred. Please try again.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \uc7a0\uc2dc \ud6c4\uc5d0 \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.",
    "April": "4\uc6d4",
    "Any divided discussion topics are divided based on cohort.": "\uad6c\ubd84\ub41c \ud1a0\ub860 \uc8fc\uc81c\uac00 \ubaa8\ub450 \uc9d1\ub2e8\uc744 \uae30\uc900\uc73c\ub85c \uad6c\ubd84\ub429\ub2c8\ub2e4.",
    "Any divided discussion topics are divided based on enrollment track.": "\uad6c\ubd84\ub41c \ud1a0\ub860 \uc8fc\uc81c\uac00 \ubaa8\ub450 \ub4f1\ub85d \ud2b8\ub799\uc744 \uae30\uc900\uc73c\ub85c \uad6c\ubd84\ub429\ub2c8\ub2e4.",
    "Are you sure you want to delete this comment?": "\uc774 \ub313\uae00\uc744 \uc0ad\uc81c\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?",
    "Are you sure you want to delete this post?": "\uc774 \uac8c\uc2dc\uae00\uc744 \uc0ad\uc81c\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?",
    "Are you sure you want to delete this response?": "\uc774 \uc751\ub2f5\uc744 \uc0ad\uc81c\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?",
    "Assign students to cohorts by uploading a CSV file.": "CSV \ud30c\uc77c\uc744 \uc5c5\ub85c\ub4dc\ud558\uc5ec \ud559\uc2b5 \uc9d1\ub2e8\uc5d0 \ud559\uc2b5\uc790\ub97c \ucd94\uac00\ud558\uc138\uc694.",
    "August": "8\uc6d4",
    "Available %s": "\uc774\uc6a9 \uac00\ub2a5\ud55c %s",
    "Blockquote": "\ube14\ub85d \uc778\uc6a9",
    "Blockquote (Ctrl+Q)": "\ube14\ub85d\uc778\uc6a9 (Ctrl+Q)",
    "Bold (Ctrl+B)": "\uc9c4\ud558\uac8c (Ctrl+B)",
    "Bulleted List (Ctrl+U)": "\uae00\uba38\ub9ac\ud45c (Ctrl+U)",
    "Cancel": "\ucde8\uc18c",
    "Cancel enrollment code": "\uc218\uac15\uc2e0\uccad \ucf54\ub4dc\ub97c \ucde8\uc18c\ud558\uc138\uc694.",
    "Change image": "\uc774\ubbf8\uc9c0 \ubcc0\uacbd",
    "Check this box to receive an email digest once a day notifying you about new, unread activity from posts you are following.": "\uc774 \ud655\uc778\ub780\uc744 \uc120\ud0dd\ud558\uba74 \ud314\ub85c\uc6b0 \uc911\uc778 \uac8c\uc2dc\uae00\uc5d0\uc11c \uc77d\uc9c0 \uc54a\uc740 \uc0c8 \ud65c\ub3d9\uc5d0 \ub300\ud574 \uc54c\ub824\uc8fc\ub294 \uc774\uba54\uc77c \uc694\uc57d\uc744 \ud558\ub8e8\uc5d0 \ud55c \ubc88\uc529 \ubc1b\uc744 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "Check your email": "\uc774\uba54\uc77c\uc744 \ud655\uc778\ud558\uc2ed\uc2dc\uc694.",
    "Checkout": "\uacb0\uc81c\ud558\uae30",
    "Checkout with PayPal": "PayPal\ub85c \uacb0\uc81c\ud558\uae30",
    "Checkout with {processor}": "{processor}\ub85c \uacb0\uc81c\ud558\uae30",
    "Choose": "\uc120\ud0dd",
    "Choose a .csv file": ".csv \ud30c\uc77c\uc744 \uc120\ud0dd\ud558\uc2ed\uc2dc\uc624. ",
    "Choose a Date": "\uc2dc\uac04 \uc120\ud0dd",
    "Choose a Time": "\uc2dc\uac04 \uc120\ud0dd",
    "Choose a time": "\uc2dc\uac04 \uc120\ud0dd",
    "Choose all": "\ubaa8\ub450 \uc120\ud0dd",
    "Chosen %s": "\uc120\ud0dd\ub41c %s",
    "Click to choose all %s at once.": "\ud55c\ubc88\uc5d0 \ubaa8\ub4e0 %s \ub97c \uc120\ud0dd\ud558\ub824\uba74 \ud074\ub9ad\ud558\uc138\uc694.",
    "Click to remove all chosen %s at once.": "\ud55c\ubc88\uc5d0 \uc120\ud0dd\ub41c \ubaa8\ub4e0 %s \ub97c \uc81c\uac70\ud558\ub824\uba74 \ud074\ub9ad\ud558\uc138\uc694.",
    "Close": "\ub2eb\uae30",
    "Closed": "\ub9c8\uac10\ub428",
    "Code Sample (Ctrl+K)": "\ucf54\ub4dc \uc0d8\ud50c (Ctrl+K)",
    "Cohort Name": "\ud559\uc2b5\uc9d1\ub2e8\uba85",
    "Cohorts": "\uc9d1\ub2e8",
    "Cohorts Disabled": "\ud559\uc2b5\uc9d1\ub2e8\uc774 \ube44\ud65c\uc131\ud654\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "Cohorts Enabled": "\ud559\uc2b5\uc9d1\ub2e8\uc774 \ud65c\uc131\ud654\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "Community TA": "\ucee4\ubba4\ub2c8\ud2f0 \uc870\uad50",
    "Confirm": "\ud655\uc778",
    "Copy Email To Editor": "\ud3b8\uc9d1\uae30\ub85c \uc774\uba54\uc77c \ubcf5\uc0ac\ud558\uae30",
    "Could not find users associated with the following identifiers:": "\ub2e4\uc74c \uc2dd\ubcc4\uc790\uc640 \uc5f0\uad00\ub41c \uc0ac\uc6a9\uc790\ub97c \ucc3e\uc744 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "Could not retrieve payment information": "\uacb0\uc81c \uc815\ubcf4\ub97c \uac80\uc0c9\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "Could not submit order": "\uc8fc\ubb38\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "Could not submit photos": "\uc0ac\uc9c4\uc744 \uc81c\ucd9c \ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "Country": "\uad6d\uac00",
    "Create an account using": "\uacc4\uc815 \uc5f0\ub3d9\ud558\uae30",
    "Creating missing groups": "\ube60\uc9c4 \uadf8\ub8f9 \ub9cc\ub4e4\uae30",
    "Current conversation": "\ud604\uc7ac \ub300\ud654",
    "Current tab": "\ud604\uc7ac \ud0ed",
    "Date": "\ub0a0\uc9dc",
    "December": "12\uc6d4",
    "Delete": "\uc0ad\uc81c",
    "Delete this team?": "\uc774 \ud300\uc744 \uc0ad\uc81c\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?",
    "Deleted Content Group": "\ucee8\ud150\uce20 \uadf8\ub8f9 \uc0ad\uc81c",
    "Deleting a team is permanent and cannot be undone. All members are removed from the team, and team discussions can no longer be accessed.": "\ud300\uc744 \uc0ad\uc81c\ud558\uba74 \uc601\uad6c\uc801\uc73c\ub85c \uc0ad\uc81c\ub418\uba70 \uc2e4\ud589 \ucde8\uc18c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ubaa8\ub4e0 \uad6c\uc131\uc6d0\uc774 \ud300\uc5d0\uc11c \uc81c\uac70\ub418\uba70 \ub354 \uc774\uc0c1 \ud300 \ud1a0\ub860\uc5d0 \uc561\uc138\uc2a4\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "Description": "\uc124\uba85",
    "Discussion": "\ud1a0\ub860",
    "Discussion Home": "\ud1a0\ub860 \ud648",
    "Discussion admins, moderators, and TAs can make their posts visible to all students or specify a single group.": "\ud1a0\ub860 \uad00\ub9ac\uc790, \uc9c4\ud589\uc790 \ubc0f \uc870\uad50\ub294 \uc790\uc2e0\uc758 \uac8c\uc2dc\uae00\uc744 \ubaa8\ub4e0 \uc218\uac15\uc790\uc5d0\uac8c \uacf5\uac1c\ud558\uac70\ub098 \ub2e8\uc77c \uadf8\ub8f9\uc744 \uacf5\uac1c \ub300\uc0c1\uc73c\ub85c \uc9c0\uc815\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "Discussion topics in the course are not divided.": "\uac15\uc758\uc758 \ud1a0\ub860 \uc8fc\uc81c\uac00 \uad6c\ubd84\ub418\uc9c0 \uc54a\uc558\uc2b5\ub2c8\ub2e4.",
    "Discussions": "\ud1a0\ub860",
    "Discussions are unified; all learners interact with posts from other learners, regardless of the group they are in.": "\ud1a0\ub860\uc774 \ud1b5\ud569\ub418\uc5b4 \uc788\uc73c\uba70 \ubaa8\ub4e0 \uc218\uac15\uc790\uac00 \uc790\uc2e0\uc774 \uc18d\ud55c \uadf8\ub8f9\uc5d0 \uad00\uacc4\uc5c6\uc774 \ub2e4\ub978 \uc218\uac15\uc790\uc758 \uac8c\uc2dc\uae00\uc5d0 \ucc38\uc5ec\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "Divided": "\uad6c\ubd84",
    "Do not show again": "\ub2e4\uc2dc \uc7ac\uc0dd\ud558\uc9c0 \ub9d0\uae30",
    "Do you want to allow this student ('{student_id}') to skip the entrance exam?": "\ud559\uc2b5\uc790 ('{student_id}')\uc758 \uc0ac\uc804 \ud3c9\uac00 \uba74\uc81c\ub97c \ud5c8\uc6a9\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?",
    "Donate": "\uae30\ubd80\ud558\uae30",
    "Double-check that your webcam is connected and working to continue.": "\uc6f9\ucea0\uc774 \uc5f0\uacb0\ub418\uc5c8\ub294\uc9c0 \uc7ac\ud655\uc778 \ud6c4\uc5d0 \uc9c4\ud589\ud574\uc8fc\uc138\uc694.",
    "Drop target image": "\ud0c0\uac9f\uc774\ubbf8\uc9c0\ub97c \ub4dc\ub86d\ud558\uc138\uc694",
    "Duration (sec)": "\uae30\uac04(\ucd08)",
    "Earn points for your engagement by adding a new post or responding to an existing post.": "\uc0c8\ub85c\uc6b4 \uac8c\uc2dc\uae00\uc744 \ucd94\uac00\ud558\uac70\ub098 \uae30\uc874 \uac8c\uc2dc\uae00\uc5d0 \uc751\ub2f5\ud558\uc5ec \ucc38\uc5ec \uc810\uc218\ub97c \ucde8\ub4dd\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "Edit": "\uc218\uc815",
    "Edit your post below.": "\uc544\ub798\uc5d0\uc11c \uac8c\uc2dc\uae00\uc744 \uc218\uc815\ud558\uc2ed\uc2dc\uc624.",
    "Editing comment": "\ub313\uae00 \uc218\uc815",
    "Editing post": "\uac8c\uc2dc\uae00 \uc218\uc815",
    "Editing response": "\uc751\ub2f5 \uc218\uc815",
    "Education Completed": "\ucd5c\uc885 \ud559\ub825",
    "Email": "\uc774\uba54\uc77c",
    "Emails successfully sent. The following users are no longer enrolled in the course:": "\uc774\uba54\uc77c \uc804\uc1a1\uc644\ub8cc. \ub2e4\uc74c \uc0ac\uc6a9\uc790\ub4e4\uc740 \uc774 \uac15\uc88c\uc5d0 \ub354\uc774\uc0c1 \ub4f1\ub85d\ub418\uc5b4 \uc788\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4:",
    "Endorse": "\uc778\uc99d",
    "Engage with posts": "\uac8c\uc2dc\uae00\uc5d0 \ucc38\uc5ec",
    "Enrolling you in the selected course": "\uc120\ud0dd\ub41c \uac15\uc88c\uc5d0 \uc218\uac15\uc2e0\uccad \ucc98\ub9ac\uc911\uc785\ub2c8\ub2e4. ",
    "Enrollment Tracks": "\ub4f1\ub85d \ud2b8\ub799",
    "Enter a student's username or email address.": "\ud559\uc2b5\uc790\uc758 \uc544\uc774\ub514 \ub610\ub294 \uc774\uba54\uc77c \uc8fc\uc18c\ub97c \uc785\ub825\ud558\uc138\uc694.",
    "Enter a username or email.": "\uc544\uc774\ub514 \ud639\uc740 \uc774\uba54\uc77c\uc744 \uc785\ub825\ud558\uc138\uc694.",
    "Enter the enrollment code.": "\uc218\uac15\uc2e0\uccad \ucf54\ub4dc\ub97c \uc785\ub825\ud558\uc138\uc694.",
    "Enter the name of the cohort": "\ud559\uc2b5\uc9d1\ub2e8\uba85\uc744 \uc785\ub825\ud558\uc138\uc694.",
    "Enter username or email": "\uc544\uc774\ub514 \ub610\ub294 \uc774\uba54\uc77c\uc744 \uc785\ub825\ud558\uc138\uc694",
    "Entrance exam attempts is being reset for student '{student_id}'.": "'{student_id}' \ud559\uc2b5\uc790\uac00 \uc2dc\ub3c4\ud55c \uc0ac\uc804 \ud3c9\uac00 \ud69f\uc218\ub294 \ucd08\uae30\ud654\ub429\ub2c8\ub2e4.",
    "Entrance exam state is being deleted for student '{student_id}'.": "\ud559\uc2b5\uc790 '{student_id}'\uc758 \uc0ac\uc804 \ud3c9\uac00 \uc0c1\ud0dc\ub294 \uc0ad\uc81c\ub429\ub2c8\ub2e4.",
    "Error": "\uc624\ub958",
    "Error adding/removing users as beta testers.": "\ubca0\ud0c0\ud14c\uc2a4\ud130 \ucd94\uac00/\uc0ad\uc81c \uc911 \uc624\ub958 \ubc1c\uc0dd",
    "Error changing user's permissions.": "\uc774\uc6a9\uc790\uc758 \uad8c\ud55c \ubcc0\uacbd \uc5d0\ub7ec",
    "Error deleting entrance exam state for student '{student_id}'. Make sure student identifier is correct.": "\ud559\uc2b5\uc790 '{student_id}'\uc758 \uc0ac\uc804 \ud3c9\uac00 \uc0c1\ud0dc\ub97c \uc0ad\uc81c\ud558\ub294 \ub3c4\uc911 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4.  \ud559\uc2b5\uc790\uc758 \uace0\uc720\ubc88\ud638\uac00 \uc62c\ubc14\ub978\uc9c0 \ud655\uc778\ud558\uc138\uc694.",
    "Error enrolling/unenrolling users.": "\uc0ac\uc6a9\uc790 \ub4f1\ub85d/\uc0ad\uc81c \uc2dc \ubc1c\uc0dd\ud55c \uc624\ub958",
    "Error generating grades. Please try again.": "\uc131\uc801 \uc0dd\uc131 \uc911 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.",
    "Error generating list of students who may enroll. Please try again.": "\uc218\uac15\uc2e0\uccad\ud55c \ud559\uc2b5\uc790 \ubaa9\ub85d\uc744 \uc0dd\uc131\ud558\ub294 \uc911 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.",
    "Error generating problem grade report. Please try again.": "\uc131\uc801 \ubcf4\uace0\uc11c \uc0dd\uc131 \uc911 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.",
    "Error generating student profile information. Please try again.": "\ud559\uc2b5\uc790 \uc815\ubcf4\ub97c \ub9cc\ub4dc\ub294 \uc911 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.",
    "Error getting entrance exam task history for student '{student_id}'. Make sure student identifier is correct.": "\ud559\uc2b5\uc790 '{student_id}'\uc758 \uc0ac\uc804 \ud3c9\uac00\uc758 \uacfc\uc81c\uc774\ub825\uc744 \uc0ad\uc81c\ud558\ub294 \ub3c4\uc911 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ud559\uc2b5\uc790\uc758 \uace0\uc720\ubc88\ud638\uac00 \uc62c\ubc14\ub978\uc9c0 \ud655\uc778\ud558\uc138\uc694.",
    "Error getting student list.": "\ud559\uc2b5\uc790 \ubaa9\ub85d \uac00\uc838\uc624\uae30 \uc5d0\ub7ec.",
    "Error listing task history for this student and problem.": "\ud559\uc2b5\uc790 \ubc0f \ubb38\uc81c \ub300\ud55c \uc791\uc5c5 \uc624\ub958 \ub0b4\uc5ed \ud45c\uc2dc\uc5d0\uc11c \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4.",
    "Error posting your message.": "\uba54\uc2dc\uc9c0\ub97c \uac8c\uc2dc\ud558\ub294 \uc911\uc5d0 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4.",
    "Error resetting entrance exam attempts for student '{student_id}'. Make sure student identifier is correct.": " '{student_id}' \ud559\uc2b5\uc790\uc758 \uc0ac\uc804 \ud3c9\uac00 \ucd08\uae30\ud654\uc5d0 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ud559\uc2b5\uc790 ID\uac00 \uc815\ud655\ud55c\uc9c0 \ud655\uc778\ud558\uc138\uc694.",
    "Error retrieving grading configuration.": "\uc131\uc801\uc124\uc815 \uac00\uc838\uc624\uae30 \uc5d0\ub7ec",
    "Error sending email.": "\uba54\uc77c \uc804\uc1a1 \uc624\ub958",
    "Error starting a task to rescore entrance exam for student '{student_id}'. Make sure that entrance exam has problems in it and student identifier is correct.": " '{student_id}' \ud559\uc2b5\uc790\uc758 \uc0ac\uc804 \ud3c9\uac00 \uc7ac\ucc44\uc810\uc5d0 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \uc0ac\uc804 \ud3c9\uac00\uc5d0 \ubb38\ud56d\uc774 \uc788\ub294\uc9c0\uc640 \ud559\uc2b5\uc790 \uc544\uc774\ub514\uac00 \uc815\ud655\ud55c\uc9c0 \ud655\uc778\ud558\uc138\uc694.",
    "Error while generating certificates. Please try again.": "\uac15\uc88c \uc774\uc218\uc99d\uc744 \ubc1c\uae09\ud558\ub294 \ub3d9\uc548 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uc138\uc694.",
    "Error:": "\uc624\ub958:",
    "Error: You cannot remove yourself from the Instructor group!": "\uc624\ub958: \uc790\uc2e0\uc744 \uad50\uc218\uc790 \uadf8\ub8f9\uc5d0\uc11c \uc81c\uac70\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. ",
    "Errors": "\uc624\ub958",
    "February": "2\uc6d4",
    "File Name": "\ud30c\uc77c\uc774\ub984",
    "Filter": "\ud544\ud130",
    "Follow": "\ud314\ub85c\uc6b0",
    "Follow or unfollow posts": "\uac8c\uc2dc\uae00 \ud314\ub85c\uc6b0 \ub610\ub294 \ud314\ub85c\uc6b0 \ucde8\uc18c",
    "Following": "\ud314\ub85c\uc789",
    "Filter and sort topics": "\uc8fc\uc81c \ud544\ud130\ub9c1 \ubc0f \ubd84\ub958",
    "Find discussions": "\ud1a0\ub860 \ucc3e\uae30",
    "Full Name": "\uc2e4\uba85",
    "Gender": "\uc131 ",
    "Heading": "\uc81c\ubaa9",
    "Heading (Ctrl+H)": "\uc81c\ubaa9 (Ctrl+H)",
    "Hide": "\uac10\ucd94\uae30",
    "Hide Discussion": "\ud1a0\ub860 \uc228\uae40",
    "Hide notes": "\ub178\ud2b8 \uac10\ucd94\uae30",
    "Horizontal Rule (Ctrl+R)": "\uac00\ub85c\uc120 (Ctrl+R)",
    "How to use %(platform_name)s discussions": "%(platform_name)s \ud1a0\ub860 \uc0ac\uc6a9 \ubc29\ubc95",
    "How to use discussions": "\ud1a0\ub860 \uc0ac\uc6a9 \ubc29\ubc95",
    "Hyperlink (Ctrl+L)": "\ud558\uc774\ud37c\ub9c1\ud06c (Ctrl+L)",
    "If you leave, you can no longer post in this team's discussions. Your place will be available to another learner.": "\ud0c8\ud1f4\ud558\uba74 \ub354 \uc774\uc0c1 \uc774 \ud300\uc758 \ud1a0\ub860\uc5d0 \uac8c\uc2dc\uae00\uc744 \uc791\uc131\ud560 \uc218 \uc5c6\uc73c\uba70 \ub0b4 \uc9c0\uc704\ub294 \ub2e4\ub978 \uc218\uac15\uc790\uc5d0\uac8c \uc81c\uacf5\ub429\ub2c8\ub2e4.",
    "Image": "\uc774\ubbf8\uc9c0",
    "Image (Ctrl+G)": "\uc774\ubbf8\uc9c0 (Ctrl+G)",
    "Image Upload Error": "\uc774\ubbf8\uc9c0 \uc5c5\ub85c\ub4dc \uc624\ub958",
    "In Progress": "\uc9c4\ud589 \uc911",
    "Insert Hyperlink": "\ud558\uc774\ud37c\ub9c1\ud06c \uc0bd\uc785",
    "Italic (Ctrl+I)": "\uae30\uc6b8\uc784 (Ctrl+I)",
    "January": "1\uc6d4",
    "July": "7\uc6d4",
    "June": "6\uc6d4",
    "KB": "KB",
    "Language": "\uc5b8\uc5b4",
    "Less": "\uc801\uac8c",
    "Linking": "\uc5f0\uacb0\ud558\uae30",
    "Links are generated on demand and expire within 5 minutes due to the sensitive nature of student information.": "\uc694\uccad\uc5d0 \uc758\ud574 \uc0dd\uc131\ub41c \ub9c1\ud06c\ub294 \ud559\uc2b5\uc790 \uc815\ubcf4 \ubcf4\ud638\ub97c \uc704\ud574  5\ubd84 \ub0b4\uc5d0 \uc18c\uba78\ub429\ub2c8\ub2e4.",
    "List item": "\ubb38\ub2e8\ubc88\ud638",
    "Load all responses": "\ubaa8\ub4e0 \uc751\ub2f5 \ub85c\ub4dc",
    "Load more": "\ub354\ubcf4\uae30",
    "Load next {numResponses} responses": "\ub2e4\uc74c {numResponses}\uac1c \uc751\ub2f5 \ub85c\ub4dc",
    "Loading": "\ub85c\ub529",
    "Loading content": "\ucf58\ud150\uce20 \ub85c\ub4dc \uc911",
    "Loading more threads": "\ucd94\uac00 \uc2a4\ub808\ub4dc \ub85c\ub4dc \uc911",
    "Loading posts list": "\uac8c\uc2dc\uae00 \ubaa9\ub85d \ub85c\ub4dc \uc911",
    "Loading your courses": "\uac15\uc88c\ub97c \ubd88\ub7ec\uc624\uace0 \uc788\uc2b5\ub2c8\ub2e4.",
    "Location in Course": "\uac15\uc88c\uc758 \uc704\uce58",
    "MB": "MB",
    "Mark as Answer": "\ub2f5\ubcc0\uc73c\ub85c \ud45c\uc2dc",
    "March": "3\uc6d4",
    "Mark enrollment code as unused": "\uc0ac\uc6a9\ub418\uc9c0 \uc54a\uc740 \uc218\uac15 \uc2e0\uccad \ucf54\ub4dc\ub97c \ud45c\uc2dc\ud558\uc138\uc694.",
    "Markdown Editing Help": "Markdow \ud3b8\uc9d1 \ub3c4\uc6c0\ub9d0",
    "May": "5\uc6d4",
    "Message:": "\ubcf8\ubb38: ",
    "Midnight": "\uc790\uc815",
    "Module state successfully deleted.": "\ubaa8\ub4c8 \uc0c1\ud0dc\uac00 \uc131\uacf5\uc801\uc73c\ub85c \uc0ad\uc81c\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "More": "\ub354\ubcf4\uae30",
    "New Address": "\uc0c8 \uc8fc\uc18c",
    "No Content Group": "\ucf58\ud150\uce20 \uadf8\ub8f9 \uc5c6\uc74c",
    "No Flash Detected": "\ud50c\ub798\uc2dc \ubbf8\uac10\uc9c0",
    "No Webcam Detected": "\uc6f9\ucea0 \ubbf8\uac10\uc9c0",
    "No posts matched your query.": "\uc9c8\uc758\uc640 \uc77c\uce58\ud558\ub294 \uac8c\uc2dc\uae00\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "No results found for \"%(query_string)s\". Please try searching again.": "\"%(query_string)s\"\ub85c \uac80\uc0c9\ub41c \uacb0\uacfc\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uac80\uc0c9\ud558\uc138\uc694.",
    "No results found for {original_query}. Showing results for {suggested_query}.": "{original_query}\uc5d0 \ub300\ud55c \uacb0\uacfc\uac00 \uc5c6\uc2b5\ub2c8\ub2e4. {suggested_query}\uc5d0 \ub300\ud55c \uacb0\uacfc\ub97c \ud45c\uc2dc\ud569\ub2c8\ub2e4.",
    "No tasks currently running.": "\uc791\uc5c5\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "Noon": "\uc815\uc624",
    "Note: You are %s hour ahead of server time.": [
      "Note: \uc11c\ubc84 \uc2dc\uac04\ubcf4\ub2e4 %s \uc2dc\uac04 \ube60\ub985\ub2c8\ub2e4."
    ],
    "Note: You are %s hour behind server time.": [
      "Note: \uc11c\ubc84 \uc2dc\uac04\ubcf4\ub2e4 %s \uc2dc\uac04 \ub2a6\uc740 \uc2dc\uac04\uc785\ub2c8\ub2e4."
    ],
    "Not divided": "\ubbf8\uad6c\ubd84",
    "Notes hidden": "\uac10\ucdb0\uc9c4 \ub178\ud2b8",
    "Notes visible": "\ubcfc \uc218 \uc788\ub294 \ub178\ud2b8",
    "November": "11\uc6d4",
    "Now": "\ud604\uc7ac",
    "Number Sent": "\ubcf4\ub0b8 \ud69f\uc218",
    "Number of Students": "\ud559\uc2b5\uc790 \uc218 ",
    "Numbered List (Ctrl+O)": "\ubb38\ub2e8 \ubc88\ud638 (Ctrl+O)",
    "OK": "\ud655\uc778",
    "October": "10\uc6d4",
    "Only properly formatted .csv files will be accepted.": "\uc801\ud569\ud55c .csv \ud30c\uc77c\ub9cc \uc62c\ub9b4 \uc218 \uc788\uc2b5\ub2c8\ub2e4. ",
    "Open": "\uc5f4\uae30",
    "Open Calculator": "\uacc4\uc0b0\uae30 \uc5f4\uae30",
    "Order No.": "\uc8fc\ubb38 \ubc88\ud638",
    "Password": "\ube44\ubc00\ubc88\ud638",
    "Photo Captured successfully.": "\uc0ac\uc9c4\uc774 \uc131\uacf5\uc801\uc73c\ub85c \ucea1\uccd0\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "Pin": "\uace0\uc815",
    "Pinned": "\uace0\uc815\ub428",
    "Placeholder": "\ud50c\ub808\uc774\uc2a4\ud640\ub354",
    "Please enter a problem location.": "\ubb38\uc81c \uc704\uce58\ub97c \uc785\ub825\ud558\uc138\uc694.",
    "Please enter a student email address or username.": "\ud559\uc2b5\uc790\uc758 \uc774\uba54\uc77c \uc8fc\uc18c\ub098 \uc544\uc774\ub514\ub97c \uc785\ub825\ud558\uc138\uc694.",
    "Please enter a username or email.": "\uc544\uc774\ub514 \ub610\ub294 \uc774\uba54\uc77c\uc744 \uc785\ub825\ud558\uc138\uc694",
    "Please enter a valid donation amount.": "\uc720\ud6a8\ud55c \uae30\ubd80 \uae08\uc561\uc744 \uc785\ub825\ud558\uc2ed\uc2dc\uc624.",
    "Please verify that you have uploaded a valid image (PNG and JPEG).": "\uc801\ud569\ud55c \uc774\ubbf8\uc9c0 \ud615\uc2dd(PNG \ubc0f JPEG)\uc778\uc9c0 \ud655\uc778\ud574 \uc8fc\uc2ed\uc2dc\uc624.",
    "Please verify that your webcam is connected and that you have allowed your browser to access it.": "\uc6f9\ucea0\uc774 \uc5f0\uacb0\ub418\uc5b4 \uc788\ub294\uc9c0, \ube0c\ub77c\uc6b0\uc800\uac00 \uc561\uc138\uc2a4\ub97c \ud5c8\uc6a9\ud558\ub294\uc9c0 \ud655\uc778\ud558\uc138\uc694.",
    "Preferred Language": "\uc120\ud638\ud558\ub294 \uc5b8\uc5b4",
    "Post type": "\uac8c\uc2dc\uae00 \uc720\ud615",
    "Prevent students from generating certificates in this course?": "\ud559\uc2b5\uc790\uc758 \uc774\uc218\uc99d \uc0dd\uc131\uc744 \uc81c\ud55c\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?",
    "Previous": "\uc774\uc804",
    "Professional Education": "\uc804\ubb38 \uad50\uc721 \uacfc\uc815",
    "Professional Education Verified Certificate": "\uc804\ubb38 \uacfc\uc815 \uc774\uc218\uc99d",
    "Question": "\uc9c8\ubb38",
    "Questions raise issues that need answers. Discussions share ideas and start conversations.": "\uc9c8\ubb38\uc744 \ud1b5\ud574 \ub2f5\ubcc0\uc744 \ud544\uc694\ub85c \ud558\ub294 \ubb38\uc81c\ub97c \uc81c\uae30\ud560 \uc218 \uc788\uc73c\uba70, \ud1a0\ub860\uc744 \ud1b5\ud574 \uc758\uacac\uc744 \uacf5\uc720\ud558\uace0 \ub300\ud654\ub97c \uc2dc\uc791\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "Questions raise issues that need answers. Discussions share ideas and start conversations. (Required)": "\uc9c8\ubb38\uc744 \ud1b5\ud574 \ub2f5\ubcc0\uc744 \ud544\uc694\ub85c \ud558\ub294 \ubb38\uc81c\ub97c \uc81c\uae30\ud560 \uc218 \uc788\uc73c\uba70, \ud1a0\ub860\uc744 \ud1b5\ud574 \uc758\uacac\uc744 \uacf5\uc720\ud558\uace0 \ub300\ud654\ub97c \uc2dc\uc791\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4(\ud544\uc218).",
    "Reason field should not be left blank.": "\uc774\uc720\ub97c \uc785\ub825\ud558\ub294 \ud544\ub4dc\ub294 \ube44\uc6cc\ub458 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "Receive updates": "\uc5c5\ub370\uc774\ud2b8 \ubc1b\uae30",
    "Recent Activity": "\ucd5c\uadfc \ud65c\ub3d9",
    "Redo (Ctrl+Shift+Z)": "\ub2e4\uc2dc\uc2e4\ud589 (Ctrl+Shift+Z)",
    "Redo (Ctrl+Y)": "\ub2e4\uc2dc\uc2e4\ud589 (Ctrl+Y)",
    "Related to: %(courseware_title_linked)s": "\uad00\ub828 \uac15\uc758 \uc790\ub8cc: %(courseware_title_linked)s",
    "Removal is in progress. To avoid errors, stay on this page until the process is complete.": "\uc0ad\uc81c\uac00 \uc9c4\ud589 \uc911\uc785\ub2c8\ub2e4. \uc624\ub958 \ubc1c\uc0dd\uc744 \ubc29\uc9c0\ud558\uae30 \uc704\ud574 \uc644\ub8cc\ub420 \ub54c\uae4c\uc9c0 \ubcf8 \ud398\uc774\uc9c0\uc5d0 \uba38\ubb3c\ub7ec \uc8fc\uc2ed\uc2dc\uc624. ",
    "Remove": "\uc81c\uac70",
    "Remove all": "\ubaa8\ub450 \uc81c\uac70",
    "Removing": "\uc81c\uac70\ud558\uae30",
    "Report": "\uc2e0\uace0",
    "Report abuse": "\ub0a8\uc6a9 \uc2e0\uace0",
    "Report abuse, topics, and responses": "\ub0a8\uc6a9, \uc8fc\uc81c \ubc0f \uc751\ub2f5 \uc2e0\uace0",
    "Reported": "\uc2e0\uace0\ub428",
    "Requester": "\uc694\uccad\uc790",
    "Reset Password": "\ube44\ubc00\ubc88\ud638 \uc7ac\uc124\uc815",
    "Reset my password": "\ube44\ubc00\ubc88\ud638 \uc7ac\uc124\uc815",
    "Responses could not be loaded. Refresh the page and try again.": "\uc751\ub2f5\uc744 \ub85c\ub4dc\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "Restore enrollment code": "\uc218\uac15\uc2e0\uccad \ucf54\ub4dc\ub97c \ubcf5\uad6c\ud558\uc138\uc694.",
    "Review your info": "\uc785\ub825 \uc815\ubcf4\ub97c \ud655\uc778\ud558\uc138\uc694.",
    "Revoke access": "\uc811\uadfc \uad8c\ud55c \ucde8\uc18c",
    "Save": "\uc800\uc7a5",
    "Save changes": "\ubcc0\uacbd\uc0ac\ud56d \uc800\uc7a5",
    "Saved cohort": "\ud559\uc2b5 \uc9d1\ub2e8\uc774 \uc800\uc7a5\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "Saving": "\uc800\uc7a5\uc911",
    "Saving your email preference": "\uc6d0\ud558\ub294 \uc774\uba54\uc77c\uc744 \uc800\uc7a5\uc911\uc785\ub2c8\ub2e4. ",
    "Search Results": "\uac80\uc0c9 \uacb0\uacfc",
    "Search all posts": "\ubaa8\ub4e0 \uac8c\uc2dc\uae00 \uac80\uc0c9",
    "Search and filter all posts to find specific topics or posts.": "\ubaa8\ub4e0 \uac8c\uc2dc\uae00\uc744 \uac80\uc0c9 \ubc0f \ud544\ud130\ub9c1\ud558\uc5ec \ud2b9\uc815 \uc8fc\uc81c \ub610\ub294 \uac8c\uc2dc\uae00\uc744 \ucc3e\uc744 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "See all teams in your course, organized by topic. Join a team to collaborate with other learners who are interested in the same topic as you are.": "\uac15\uc88c\uc5d0\uc11c \uc8fc\uc81c\ubcc4\ub85c \uc870\uc9c1\ub41c \ubaa8\ub4e0 \ud300\uc744 \ubcf4\uc138\uc694. \uad00\uc2ec\uc0ac\uac00 \uac19\uc740 \ub2e4\ub978 \ud559\uc2b5\uc790\ub4e4\uacfc \ud611\ub825\ud558\uae30 \uc704\ud574 \ud300\uc5d0 \ucc38\uc5ec\ud558\uc138\uc694.",
    "Select a chapter": "chapter \uc120\ud0dd",
    "Selected tab": "\uc120\ud0dd\ub41c \ud0ed",
    "Sent By": "\ubcf4\ub0b8 \uc0ac\ub78c",
    "Sent By:": "\ubcf4\ub0b4\ub294 \uc0ac\ub78c:",
    "Sent To:": "\ubc1b\ub294\uc0ac\ub78c:",
    "September": "9\uc6d4",
    "Settings": "\uc124\uc815",
    "Show": "\ubcf4\uae30",
    "Show Comment (%(num_comments)s)": [
      "\ub313\uae00 \ud45c\uc2dc(%(num_comments)s\uac1c)"
    ],
    "Show Discussion": "\ud1a0\ub860 \ud45c\uc2dc",
    "Show notes": "\ub178\ud2b8 \ubcf4\uc774\uae30",
    "Show posts by {username}.": "{username}\ub2d8\uc774 \uc791\uc131\ud55c \uac8c\uc2dc\uae00\uc744 \ud45c\uc2dc\ud569\ub2c8\ub2e4.",
    "Showing all responses": "\ubaa8\ub4e0 \uc751\ub2f5 \ud45c\uc2dc \uc911",
    "Showing first response": [
      "\uccab \ubc88\uc9f8 \uc751\ub2f5 \ud45c\uc2dc \uc911"
    ],
    "Sign in": "\ub85c\uadf8\uc778",
    "Some images in this post have been omitted": "\uc774 \uac8c\uc2dc\uae00\uc758 \uc77c\ubd80 \uc774\ubbf8\uc9c0\uac00 \uc0dd\ub7b5\ub428",
    "Staff": "\uc9c1\uc6d0",
    "Start generating certificates for all students in this course?": "\ubcf8 \uac15\uc88c\uc758 \ubaa8\ub4e0 \ud559\uc2b5\uc790\ub97c \uc704\ud55c \uac15\uc88c \uc774\uc218\uc99d \uc0dd\uc131\uc744 \uc2dc\uc791\ud558\uc2dc\uaca0\uc2b5\ub2c8\uae4c?",
    "Starts": "\uac1c\uac15\uc77c",
    "State": "\uc0c1\ud0dc",
    "Status": "\uc0c1\ud0dc",
    "Subject": "\uc81c\ubaa9",
    "Subject:": "\uc81c\ubaa9:",
    "Submit": "\uc81c\ucd9c",
    "Submitted": "\uc81c\ucd9c\ud588\uc2b5\ub2c8\ub2e4.",
    "Success": "\uc131\uacf5",
    "Successfully deleted student state for user {user}": " {user} \ud559\uc2b5\uc790 \uc0c1\ud0dc \uc0ad\uc81c \uc131\uacf5",
    "Successfully enrolled and sent email to the following users:": "\uc131\uacf5\uc801\uc73c\ub85c \ub4f1\ub85d\ud558\uace0, \ub2e4\uc74c \uc774\uc6a9\uc790\uc5d0\uac8c \uc774\uba54\uc77c\uc744 \ubc1c\uc1a1\ud588\uc2b5\ub2c8\ub2e4. ",
    "Successfully enrolled the following users:": "\ub2e4\uc74c \uc774\uc6a9\uc790\ub4e4\uc744 \uc131\uacf5\uc801\uc73c\ub85c \ub4f1\ub85d\ud588\uc2b5\ub2c8\ub2e4.",
    "Successfully rescored problem for user {user}": "{user} \uc774\uc6a9\uc790\uc758 \ubb38\uc81c\uac00 \uc7ac\ucc44\uc810 \ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "Successfully reset the attempts for user {user}": "{user} \uc774\uc6a9\uc790\uc758 \uc2dc\ub3c4\ub97c \ucd08\uae30\ud654 \ud558\uc600\uc2b5\ub2c8\ub2e4.",
    "Successfully sent enrollment emails to the following users. They will be allowed to enroll once they register:": "\ub4f1\ub85d \uc774\uba54\uc77c\uc744 \ub2e4\uc74c \uc774\uc6a9\uc790\ub4e4\uc5d0\uac8c  \ubc1c\uc1a1\ud588\uc2b5\ub2c8\ub2e4. ",
    "Successfully sent enrollment emails to the following users. They will be enrolled once they register:": "\ub2e4\uc74c \uc0ac\uc6a9\uc790\uc5d0\uac8c  \uc131\uacf5\uc801\uc73c\ub85c \ub4f1\ub85d \uc774\uba54\uc77c\uc744 \ubc1c\uc1a1\ud588\uc2b5\ub2c8\ub2e4. \uac00\uc785\uc2e0\uccad\ud558\uba74 \uac15\uc88c\uc5d0 \ub4f1\ub85d\uc774 \ub420 \uac83\uc785\ub2c8\ub2e4: ",
    "Successfully unlinked.": "\uc131\uacf5\uc801 \uc5f0\uacb0\uc774 \ud574\uc81c\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "Tags": "Tags",
    "Take Photo": "\uc0ac\uc9c4 \ucd2c\uc601",
    "Take a photo of your ID": "\uc2e0\ubd84\uc99d \uc0ac\uc9c4\uc744 \ucc0d\uc5b4 \uc8fc\uc138\uc694.",
    "Task ID": "\uc791\uc5c5 ID",
    "Task Progress": "\uc791\uc5c5 \uc9c4\ud589\uc0c1\ud669",
    "Task Status": "\uc791\uc5c5 \uc0c1\ud0dc",
    "Task Type": "\uc791\uc5c5 \uc720\ud615",
    "Task inputs": "\uc791\uc5c5 \uc785\ub825",
    "Team \"{team}\" successfully deleted.": "\ud300 \"{team}\"\uc774(\uac00) \uc131\uacf5\uc801\uc73c\ub85c \uc0ad\uc81c\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "Teams": "\ud300",
    "The cohort cannot be added": "\ud559\uc2b5 \uc9d1\ub2e8\uc774 \ucd94\uac00\ub420 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "The cohort cannot be saved": "\ud559\uc2b5 \uc9d1\ub2e8\uc774 \uc800\uc7a5\ub420 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "The file must be at least {size} in size.": "\ud30c\uc77c\uc758 \ud06c\uae30\uac00 \uc801\uc5b4\ub3c4 {size} \uc5ec\uc57c \ud569\ub2c8\ub2e4. ",
    "The file must be smaller than {size} in size.": "\ud30c\uc77c\uc758 \ud06c\uae30\uac00 {size} \ubcf4\ub2e4 \uc791\uc544\uc57c \ud569\ub2c8\ub2e4. ",
    "The following email addresses and/or usernames are invalid:": "\ub2e4\uc74c\uc758 \uc774\uba54\uc77c \uc8fc\uc18c  \ub610\ub294 \uc544\uc774\ub514\ub294 \uc720\ud6a8\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4. ",
    "The following errors were generated:": "\ub2e4\uc74c \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4.",
    "The following users are no longer enrolled in the course:": "\ub2e4\uc74c \uc0ac\uc6a9\uc790\ub4e4\uc740 \uc774 \uac15\uc88c\uc5d0 \ub354\uc774\uc0c1 \ub4f1\ub85d\ub418\uc5b4 \uc788\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4:",
    "The following warnings were generated:": "\ub2e4\uc74c \uacbd\uace0\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4:",
    "The post you selected has been deleted.": "\uc120\ud0dd\ud558\uc2e0 \uac8c\uc2dc\uae00\uc740 \uc0ad\uc81c\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "The selected content group does not exist": "\uc120\ud0dd\ub41c \ucf58\ud150\uce20 \uadf8\ub8f9\uc774 \uc874\uc7ac\ud558\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.",
    "The {cohortGroupName} cohort has been created. You can manually add students to this cohort below.": "{cohortGroupName} \ud559\uc2b5\uc9d1\ub2e8\uc774 \uc0dd\uc131\ub418\uc5c8\uc2b5\ub2c8\ub2e4. \uc218\uc791\uc5c5\uc73c\ub85c \ud559\uc2b5\uc790\ub97c \ucd94\uac00\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4. ",
    "There has been an error processing your survey.": "\uc124\ubb38\uc744 \ucc98\ub9ac\ud558\ub294 \ub3d9\uc548 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4.",
    "There is no email history for this course.": "\uc774 \uac15\uc88c\uc5d0\ub294 \uba54\uc77c \uc804\uc1a1 \uae30\ub85d\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "There was a problem creating the report. Select \"Create Executive Summary\" to try again.": "\ubcf4\uace0\uc11c\ub97c \uc0dd\uc131\ud558\ub294 \ub3d9\uc548 \ubb38\uc81c\uac00 \uc788\uc5c8\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uc2dc\ub3c4\ud558\uae30 \uc704\ud574 Create Executive Summary\ub97c \uc120\ud0dd\ud558\uc138\uc694.",
    "There was an error obtaining email content history for this course.": "\uc774 \uac15\uc88c\uc758 \uba54\uc77c \uc804\uc1a1 \uae30\ub85d\uc744 \uac00\uc838\uc624\ub294\ub370 \uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4.",
    "There was an error obtaining email task history for this course.": "\uc774 \uac15\uc88c\uc758 \uc774\uba54\uc77c \ubc1c\uc1a1 \uae30\ub85d \uac00\uc838\uc624\uae30\uc5d0 \uc2e4\ud328\ud558\uc600\uc2b5\ub2c8\ub2e4.",
    "There was an error, try searching again.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ub2e4\uc2dc \uac80\uc0c9\ud558\uc138\uc694.",
    "These users were not added as beta testers:": "\uc774 \uc774\uc6a9\uc790\ub4e4\uc740  \ubca0\ud0c0\ud14c\uc2a4\ud130\ub85c \ucd94\uac00\ub418\uc9c0 \uc54a\uc558\uc2b5\ub2c8\ub2e4.",
    "These users were not affiliated with the course so could not be unenrolled:": "\uc774 \uc0ac\uc6a9\uc790\ub4e4\uc740 \uc774 \uac15\uc88c\uc640 \uad00\ub828\uc5c6\uc73c\ubbc0\ub85c \uc218\uac15\ucde8\uc18c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "These users were not removed as beta testers:": "\uc774 \uc774\uc6a9\uc790\ub4e4\uc740 \ubca0\ud0c0\ud14c\uc2a4\ud130\uc5d0\uc11c \uc0ad\uc81c\ub418\uc9c0 \uc54a\uc558\uc2b5\ub2c8\ub2e4.",
    "These users were successfully added as beta testers:": "\uc774 \uc774\uc6a9\uc790\ub4e4\uc774 \uc131\uacf5\uc801\uc73c\ub85c \ubca0\ud0c0\ud14c\uc2a4\ud130\ub85c \ucd94\uac00\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "These users were successfully removed as beta testers:": "\uc774 \uc774\uc6a9\uc790\ub4e4\uc774 \uc131\uacf5\uc801\uc73c\ub85c \ubca0\ud0c0\ud14c\uc2a4\ud130\uc5d0\uc11c \uc0ad\uc81c\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "These users will be allowed to enroll once they register:": "\uc774 \uc0ac\uc6a9\uc790\ub4e4\uc740 \ub4f1\ub85d\ud558\uba74 \ubc14\ub85c \uc218\uac15\uc2e0\uccad\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4. ",
    "These users will be enrolled once they register:": "\uac00\uc785 \uc2e0\uccad\ud558\uba74 \uac15\uc88c\uc5d0 \ub4f1\ub85d\uc774 \ub420 \uac83\uc785\ub2c8\ub2e4: ",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "\uc0ac\uc6a9 \uac00\ub2a5\ud55c %s \uc758 \ub9ac\uc2a4\ud2b8 \uc785\ub2c8\ub2e4.  \uc544\ub798\uc758 \uc0c1\uc790\uc5d0\uc11c \uc120\ud0dd\ud558\uace0 \ub450 \uc0c1\uc790 \uc0ac\uc774\uc758 \"\uc120\ud0dd\" \ud654\uc0b4\ud45c\ub97c \ud074\ub9ad\ud558\uc5ec \uba87 \uac00\uc9c0\ub97c \uc120\ud0dd\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "\uc120\ud0dd\ub41c %s \ub9ac\uc2a4\ud2b8 \uc785\ub2c8\ub2e4.  \uc544\ub798\uc758 \uc0c1\uc790\uc5d0\uc11c \uc120\ud0dd\ud558\uace0 \ub450 \uc0c1\uc790 \uc0ac\uc774\uc758 \"\uc81c\uac70\" \ud654\uc0b4\ud45c\ub97c \ud074\ub9ad\ud558\uc5ec \uc77c\ubd80\ub97c \uc81c\uac70 \ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "This comment could not be deleted. Refresh the page and try again.": "\uc774 \ub313\uae00\uc744 \uc0ad\uc81c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This discussion could not be loaded. Refresh the page and try again.": "\uc774 \ud1a0\ub860\uc744 \ub85c\ub4dc\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This post could not be closed. Refresh the page and try again.": "\uc774 \uac8c\uc2dc\uae00\uc744 \ub2eb\uc744 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This post could not be flagged for abuse. Refresh the page and try again.": "\uc774 \uac8c\uc2dc\uae00\uc744 \ub0a8\uc6a9\uc73c\ub85c \uc2e0\uace0\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This post could not be pinned. Refresh the page and try again.": "\uc774 \uac8c\uc2dc\uae00\uc744 \uace0\uc815\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This post could not be reopened. Refresh the page and try again.": "\uc774 \uac8c\uc2dc\uae00\uc744 \ub2e4\uc2dc \uc5f4 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This post could not be unflagged for abuse. Refresh the page and try again.": "\uc774 \uac8c\uc2dc\uae00\uc5d0 \ub300\ud55c \ub0a8\uc6a9 \uc2e0\uace0\ub97c \ucde8\uc18c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This post could not be unpinned. Refresh the page and try again.": "\uc774 \uac8c\uc2dc\uae00\uc744 \uace0\uc815 \ucde8\uc18c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This post is visible only to %(group_name)s.": "%(group_name)s\uc5d0\uac8c\ub9cc \uacf5\uac1c\ub41c \uac8c\uc2dc\uae00\uc785\ub2c8\ub2e4.",
    "This post is visible to everyone.": "\ubaa8\ub4e0 \uc0ac\uc6a9\uc790\uc5d0\uac8c \uacf5\uac1c\ub41c \uac8c\uc2dc\uae00\uc785\ub2c8\ub2e4.",
    "This response could not be marked as an answer. Refresh the page and try again.": "\uc774 \uc751\ub2f5\uc744 \ub2f5\ubcc0\uc73c\ub85c \ud45c\uc2dc\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This response could not be marked as endorsed. Refresh the page and try again.": "\uc774 \uc751\ub2f5\uc744 \uc778\uc99d \ud45c\uc2dc\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This response could not be unendorsed. Refresh the page and try again.": "\uc774 \uc751\ub2f5\uc744 \uc778\uc99d \ucde8\uc18c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This response could not be unmarked as an answer. Refresh the page and try again.": "\uc774 \uc751\ub2f5\uc744 \ub2f5\ubcc0 \ud45c\uc2dc \ud574\uc81c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "This thread is closed.": "\uc774 \uc2a4\ub808\ub4dc\ub294 \ub9c8\uac10\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "This vote could not be processed. Refresh the page and try again.": "\uc774 \ud22c\ud45c\ub97c \ucc98\ub9ac\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "Time Sent": "\ubcf4\ub0b8 \uc2dc\uac04",
    "Time Sent:": "\ubcf4\ub0b8 \uc2dc\uac04:",
    "Today": "\uc624\ub298",
    "Tomorrow": "\ub0b4\uc77c",
    "Type into this box to filter down the list of available %s.": "\uc0ac\uc6a9 \uac00\ub2a5\ud55c %s \ub9ac\uc2a4\ud2b8\ub97c \ud544\ud130\ub9c1\ud558\ub824\uba74 \uc774 \uc0c1\uc790\uc5d0 \uc785\ub825\ud558\uc138\uc694.",
    "Toggle Notifications Setting": "\uc54c\ub9bc \uc124\uc815 \uc804\ud658",
    "Topic area": "\uc8fc\uc81c \uc601\uc5ed",
    "Undo (Ctrl+Z)": "\ub418\ub3cc\ub9ac\uae30 (Ctrl+Z)",
    "Unendorse": "\uc778\uc99d \ucde8\uc18c",
    "Unfollow": "\ud314\ub85c\uc6b0 \ucde8\uc18c",
    "Unknown": "\uc54c \uc218 \uc5c6\uc74c",
    "Unlinking": "\uc5f0\uacb0 \ud574\uc81c\ud558\uae30",
    "Unmark as Answer": "\ub2f5\ubcc0 \ud45c\uc2dc \ud574\uc81c",
    "Unpin": "\uace0\uc815 \ucde8\uc18c",
    "Unreport": "\uc2e0\uace0 \ucde8\uc18c",
    "Update comment": "\ub313\uae00 \uc5c5\ub370\uc774\ud2b8",
    "Update post": "\uac8c\uc2dc\uae00 \uc5c5\ub370\uc774\ud2b8",
    "Update response": "\uc751\ub2f5 \uc5c5\ub370\uc774\ud2b8",
    "Updating with latest library content": "\ucd5c\uc2e0 \ucf58\ud150\uce20 \ubcf4\uad00\ud568\uc73c\ub85c \uc5c5\ub370\uc774\ud2b8",
    "Upload File": "\ud30c\uc77c \uc5c5\ub85c\ub4dc",
    "Upload File and Assign Students": "\ud30c\uc77c \uc5c5\ub85c\ub4dc \ubc0f \ud559\uc2b5\uc790 \ud560\ub2f9\ud558\uae30",
    "Upload New File": "\ud30c\uc77c \uc5c5\ub85c\ub4dc",
    "Upload an image": "\uc774\ubbf8\uc9c0 \uc5c5\ub85c\ub4dc",
    "Upload is in progress. To avoid errors, stay on this page until the process is complete.": "\uc5c5\ub85c\ub4dc\uac00 \uc9c4\ud589 \uc911\uc785\ub2c8\ub2e4. \uc624\ub958 \ubc1c\uc0dd\uc744 \ubc29\uc9c0\ud558\uae30 \uc704\ud574 \uc644\ub8cc\ub420 \ub54c\uae4c\uc9c0 \ubcf8 \ud398\uc774\uc9c0\uc5d0 \uba38\ubb3c\ub7ec \uc8fc\uc2ed\uc2dc\uc624",
    "Upload signature image.": "\uc11c\uba85 \uc774\ubbf8\uc9c0 \uc5c5\ub85c\ub4dc\ud558\uae30",
    "Uploading": "\uc5c5\ub85c\ub4dc \uc911",
    "Username": "\uc544\uc774\ub514",
    "Users must create and activate their account before they can be promoted to beta tester.": "\uc774\uc6a9\uc790\ub294 \ubca0\ud0c0\ud14c\uc2a4\ud130\ub85c \ub4f1\ub85d\ub418\uae30 \uc804\uc5d0 \uacc4\uc815\uc744 \uc0dd\uc131\ud558\uace0 \ud65c\uc131\ud654\ud574\uc57c \ud569\ub2c8\ub2e4.",
    "Use cohorts as the basis for dividing discussions. All learners, regardless of cohort, see the same discussion topics, but within divided topics, only members of the same cohort see and respond to each others\u2019 posts. ": "\uc9d1\ub2e8\uc744 \ud1a0\ub860\uc744 \uad6c\ubd84\ud558\ub294 \uae30\uc900\uc73c\ub85c \uc0ac\uc6a9\ud569\ub2c8\ub2e4. \ubaa8\ub4e0 \uc218\uac15\uc790\uac00 \uc9d1\ub2e8\uc5d0 \uad00\uacc4\uc5c6\uc774 \ub3d9\uc77c\ud55c \ud1a0\ub860 \uc8fc\uc81c\ub97c \ubcfc \uc218 \uc788\uc9c0\ub9cc \uad6c\ubd84\ub41c \uc8fc\uc81c \ub0b4\uc5d0\uc11c\ub294 \ub3d9\uc77c\ud55c \uc9d1\ub2e8\uc5d0 \uc18d\ud55c \uad6c\uc131\uc6d0\ub9cc \uc11c\ub85c\uc758 \uac8c\uc2dc\uae00\uc744 \ubcf4\uace0 \ub2f5\ubcc0\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4. ",
    "Use enrollment tracks as the basis for dividing discussions. All learners, regardless of their enrollment track, see the same discussion topics, but within divided topics, only learners who are in the same enrollment track see and respond to each others\u2019 posts.": "\ub4f1\ub85d \ud2b8\ub799\uc744 \ud1a0\ub860\uc744 \uad6c\ubd84\ud558\ub294 \uae30\uc900\uc73c\ub85c \uc0ac\uc6a9\ud569\ub2c8\ub2e4. \ubaa8\ub4e0 \uc218\uac15\uc790\uac00 \uc790\uc2e0\uc758 \ub4f1\ub85d \ud2b8\ub799\uc5d0 \uad00\uacc4\uc5c6\uc774 \ub3d9\uc77c\ud55c \ud1a0\ub860 \uc8fc\uc81c\ub97c \ubcfc \uc218 \uc788\uc9c0\ub9cc \uad6c\ubd84\ub41c \uc8fc\uc81c \ub0b4\uc5d0\uc11c\ub294 \ub3d9\uc77c\ud55c \ub4f1\ub85d \ud2b8\ub799\uc5d0 \uc18d\ud55c \uc218\uac15\uc790\ub9cc \ub2e4\ub978 \uc218\uac15\uc790\uc758 \uac8c\uc2dc\uae00\uc744 \ubcf4\uace0 \ub2f5\ubcc0\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.",
    "Use the": "\ub2e4\uc74c",
    "Use the All Topics menu to find specific topics.": "\u2018\ubaa8\ub4e0 \uc8fc\uc81c\u2019 \uba54\ub274\ub97c \uc0ac\uc6a9\ud558\uc5ec \ud2b9\uc815 \uc8fc\uc81c\ub97c \ucc3e\uc73c\uc2ed\uc2dc\uc624.",
    "Validation Error": "\uc720\ud6a8\uc131 \uc5d0\ub7ec",
    "Verified Certificate": "\uc778\uc99d \uc774\uc218\uc99d",
    "Verified Certificate upgrade": "\uc778\uc99d \uc774\uc218\uc99d \uc5c5\uadf8\ub808\uc774\ub4dc\ud558\uae30",
    "Video Capture Error": "\ub3d9\uc601\uc0c1 \ucea1\uccd0 \uc624\ub958",
    "View": "\ubcf4\uae30",
    "View %(span_start)s %(team_name)s %(span_end)s": "%(span_start)s %(team_name)s %(span_end)s \ubcf4\uae30",
    "View Teams in the %(topic_name)s Topic": "%(topic_name)s \uc8fc\uc81c\uc758 \ud300 \ubcf4\uae30",
    "View all errors": "\ubaa8\ub4e0 \uc624\ub958 \ubcf4\uae30",
    "View discussion": "\ud1a0\ub860 \ubcf4\uae30",
    "Viewing %s course": [
      "%s \uac15\uc88c \ubcf4\uae30"
    ],
    "Visible to": "\uacf5\uac1c \ub300\uc0c1",
    "Vote for good posts and responses": "\uc88b\uc740 \uac8c\uc2dc\uae00 \ubc0f \uc751\ub2f5\uc5d0 \ud22c\ud45c",
    "Vote for goods post and responses": "\uc88b\uc740 \uac8c\uc2dc\uae00 \ubc0f \uc751\ub2f5\uc5d0 \ud22c\ud45c",
    "Vote for this post,": "\uc774 \uac8c\uc2dc\uae00\uc5d0 \ud22c\ud45c,",
    "Warnings": "\uacbd\uace0!",
    "We couldn't find any results for \"%s\".": "\"%s\"\ub97c \ucc3e\uc744 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. ",
    "We have encountered an error. Refresh your browser and then try again.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ube0c\ub77c\uc6b0\uc800\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "We've encountered an error. Refresh your browser and then try again.": "\uc624\ub958\uac00 \ubc1c\uc0dd\ud588\uc2b5\ub2c8\ub2e4. \ube0c\ub77c\uc6b0\uc800\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "Webcam": "\uc6f9\ucea0",
    "Year of Birth": "\ucd9c\uc0dd\uc5f0\ub3c4",
    "Yesterday": "\uc5b4\uc81c",
    "You are not permitted to view this discussion.": "\uc774 \ud1a0\ub860\uc744 \ubcfc \uad8c\ud55c\uc774 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "You could not be subscribed to this post. Refresh the page and try again.": "\uc774 \uac8c\uc2dc\uae00\uc744 \uad6c\ub3c5\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "You could not be unsubscribed from this post. Refresh the page and try again.": "\uc774 \uac8c\uc2dc\uae00\uc744 \uad6c\ub3c5 \ucde8\uc18c\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "You currently have no cohorts configured": "\uc124\uc815\ub41c \ud559\uc2b5 \uc9d1\ub2e8\uc774 \ud604\uc7ac \uc5c6\uc2b5\ub2c8\ub2e4.",
    "You did not select a content group": "\ucf58\ud150\uce20 \uadf8\ub8f9\uc744 \uc120\ud0dd\ud558\uc9c0 \uc54a\uc558\uc2b5\ub2c8\ub2e4. ",
    "You don't seem to have Flash installed. Get Flash to continue your verification.": "Flash\uac00 \uc124\uce58\ub418\uc5b4 \uc788\uc9c0 \uc54a\uc740 \uac83 \uac19\uc2b5\ub2c8\ub2e4. Flash \uc124\uce58 \ud6c4 \uacc4\uc18d \uc9c4\ud589\ud558\uc138\uc694.",
    "You don't seem to have a webcam connected.": "\uc6f9\ucea0\uc774 \uc5f0\uacb0\ub418\uc9c0 \uc54a\uc740 \uac83 \uac19\uc2b5\ub2c8\ub2e4.",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "\uac1c\ubcc4 \ud544\ub4dc\uc5d0 \uc544\ubb34\ub7f0 \ubcc0\uacbd\uc774 \uc5c6\ub294 \uc0c1\ud0dc\ub85c \uc561\uc158\uc744 \uc120\ud0dd\ud588\uc2b5\ub2c8\ub2e4. \uc800\uc7a5 \ubc84\ud2bc\uc774 \uc544\ub2c8\ub77c \uc9c4\ud589 \ubc84\ud2bc\uc744 \ucc3e\uc544\ubcf4\uc138\uc694.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "\uac1c\ubcc4 \ud544\ub4dc\uc758 \uac12\ub4e4\uc744 \uc800\uc7a5\ud558\uc9c0 \uc54a\uace0 \uc561\uc158\uc744 \uc120\ud0dd\ud588\uc2b5\ub2c8\ub2e4. OK\ub97c \ub204\ub974\uba74 \uc800\uc7a5\ub418\uba70, \uc561\uc158\uc744 \ud55c \ubc88 \ub354 \uc2e4\ud589\ud574\uc57c \ud569\ub2c8\ub2e4.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "\uac1c\ubcc4 \ud3b8\uc9d1 \uac00\ub2a5\ud55c \ud544\ub4dc\uc5d0 \uc800\uc7a5\ub418\uc9c0 \uc54a\uc740 \uac12\uc774 \uc788\uc2b5\ub2c8\ub2e4. \uc561\uc158\uc744 \uc218\ud589\ud558\uba74 \uc800\uc7a5\ub418\uc9c0 \uc54a\uc740 \uac12\ub4e4\uc744 \uc783\uc5b4\ubc84\ub9ac\uac8c \ub429\ub2c8\ub2e4.",
    "You must sign out and sign back in before your language changes take effect.": "\uc5b8\uc5b4\uac00 \ubc14\ub00c\uc5b4\uc84c\ub294\uc9c0 \ud655\uc778\ud558\uae30 \uc704\ud574 \ub85c\uadf8\uc544\uc6c3 \ud558\uace0 \ub2e4\uc2dc \ub85c\uadf8\uc778 \ud558\uc138\uc694.",
    "You must specify a name for the cohort": "\ud559\uc2b5 \uc9d1\ub2e8\uc758 \uc774\ub984\uc744 \uc785\ub825\ud574\uc57c \ud569\ub2c8\ub2e4.",
    "You've made some changes": "\uc218\uc815 \uc644\ub8cc",
    "Your changes have been saved.": "\ubcc0\uacbd \uc0ac\ud56d\uc774 \uc800\uc7a5\ub418\uc5c8\uc2b5\ub2c8\ub2e4.",
    "Your changes have been saved. {details}": "\ubcc0\uacbd \uc0ac\ud56d\uc774 \uc800\uc7a5\ub418\uc5c8\uc2b5\ub2c8\ub2e4. {details}",
    "Your changes will not take effect until you save your progress.": "\uc800\uc7a5\ud558\uae30 \uc804\uc5d0\ub294 \ubcc0\uacbd\uc0ac\ud56d\uc774 \uc801\uc6a9\ub418\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.",
    "Your donation could not be submitted.": "\uae30\ubd80 \ucc98\ub9ac\uac00 \ub420 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4.",
    "Your file '{file}' has been uploaded. Allow a few minutes for processing.": "'{file}' \ud30c\uc77c\uc774 \uc5c5\ub85c\ub4dc \ub418\uc5c8\uc2b5\ub2c8\ub2e4. \ucc98\ub9ac\ud558\ub294\ub370 \uc7a0\uc2dc \uc2dc\uac04\uc774 \ud544\uc694\ud569\ub2c8\ub2e4. ",
    "Your message cannot be blank.": "\ub0b4\uc6a9\uc744 \uc785\ub825\ud574\uc57c \ud569\ub2c8\ub2e4.",
    "Your message must have a subject.": "\uc81c\ubaa9\uc744 \uc785\ub825\ud574\uc57c \ud569\ub2c8\ub2e4.",
    "Your post will be discarded.": "\uac8c\uc2dc\uae00\uc774 \ud3d0\uae30\ub429\ub2c8\ub2e4.",
    "Your question or idea (required)": "\ub0b4 \uc9c8\ubb38 \ub610\ub294 \uc758\uacac(\ud544\uc218)",
    "Your request could not be processed. Refresh the page and try again.": "\uc694\uccad\uc744 \ucc98\ub9ac\ud560 \uc218 \uc5c6\uc2b5\ub2c8\ub2e4. \ud398\uc774\uc9c0\ub97c \uc0c8\ub85c\uace0\uce68\ud55c \ub2e4\uc74c \ub2e4\uc2dc \uc2dc\ub3c4\ud574 \ubcf4\uc2ed\uc2dc\uc624.",
    "Your upload of '{file}' failed.": "'{file}'\ud30c\uc77c \uc5c5\ub85c\ub4dc\ub97c \uc2e4\ud328\ud588\uc2b5\ub2c8\ub2e4.",
    "Your upload of '{file}' succeeded.": "'{file}'\ud30c\uc77c \uc5c5\ub85c\ub4dc\ub97c \uc131\uacf5\ud588\uc2b5\ub2c8\ub2e4.",
    "[no tags]": "[no tags]",
    "anonymous": "\uc775\uba85",
    "answered question": "\ub2f5\ubcc0\uc774 \uc788\ub294 \uc9c8\ubb38",
    "bytes": "bytes",
    "discussion": "\ud1a0\ub860",
    "discussion posted": "\ud1a0\ub860\uc774 \uac8c\uc2dc\ub428",
    "discussion posted %(time_ago)s by %(author)s": "%(time_ago)s\uc5d0 %(author)s\uc774(\uac00) \uac8c\uc2dc\ud55c \ud1a0\ub860",
    "dragging": "\ub9c8\uc6b0\uc2a4\ub85c \ub04c\uace0 \uc624\uae30",
    "dragging out of slider": "\uc2ac\ub77c\uc774\ub354 \ub2f9\uae30\uae30",
    "dropped in slider": "\uc2ac\ub77c\uc774\ub354\uc5d0 \ub5a8\uc5b4\ud2b8\ub838\uc2b5\ub2c8\ub2e4.",
    "dropped on target": "\ubaa9\ud45c\uc810\uc5d0 \ub5a8\uc5b4\ud2b8\ub838\uc2b5\ub2c8\ub2e4.",
    "emphasized text": "\uac15\uc870\ub41c \ubb38\uc7a5",
    "endorsed %(time_ago)s": "%(time_ago)s\uc5d0 \uc778\uc99d\ub428",
    "endorsed %(time_ago)s by %(user)s": "%(time_ago)s\uc5d0 %(user)s\uc774(\uac00) \uc778\uc99d\ud568",
    "engage with posts": "\uac8c\uc2dc\uae00\uc5d0 \ucc38\uc5ec",
    "enter code here": "\ucf54\ub4dc \uc785\ub825\ud558\uc138\uc694",
    "enter link description here": "\ub9c1\ud06c \uc124\uba85\uc744 \uc5ec\uae30\uc5d0 \uc785\ub825\ud558\uc138\uc694",
    "find discussions": "\ud1a0\ub860 \ucc3e\uae30",
    "follow this post": "\uc774 \uac8c\uc2dc\uae00 \ud314\ub85c\uc6b0",
    "image omitted": "\uc774\ubbf8\uc9c0 \uc0dd\ub7b5\ub428",
    "marked as answer %(time_ago)s": "%(time_ago)s\uc5d0 \ub2f5\ubcc0\uc73c\ub85c \ud45c\uc2dc\ub428",
    "marked as answer %(time_ago)s by %(user)s": "%(time_ago)s\uc5d0 %(user)s\uc774(\uac00) \ub2f5\ubcc0\uc73c\ub85c \ud45c\uc2dc\ud568",
    "name": "\uc774\ub984",
    "one letter Friday\u0004F": "\uae08",
    "one letter Monday\u0004M": "\uc6d4",
    "one letter Saturday\u0004S": "\ud1a0",
    "one letter Sunday\u0004S": "\uc77c",
    "one letter Thursday\u0004T": "\ubaa9",
    "one letter Tuesday\u0004T": "\ud654",
    "one letter Wednesday\u0004W": "\uc218",
    "post anonymously": "\uc775\uba85\uc73c\ub85c \uac8c\uc2dc",
    "post anonymously to classmates": "\uac19\uc740 \uc218\uac15\uc790\uc5d0\uac8c \uc775\uba85\uc73c\ub85c \uac8c\uc2dc",
    "posted %(time_ago)s by %(author)s": "%(time_ago)s\uc5d0 %(author)s\uc774(\uac00) \uac8c\uc2dc\ud568",
    "question posted %(time_ago)s by %(author)s": "%(time_ago)s\uc5d0 %(author)s\uc774(\uac00) \uac8c\uc2dc\ud55c \uc9c8\ubb38",
    "strong text": "\uac15\ud558\uac8c",
    "team count": "\ud300 \uc778\uc6d0 \uc218",
    "there is currently {numVotes} vote": [
      "\ud604\uc7ac {numVotes}\ud45c\ub97c \ubc1b\uc74c"
    ],
    "unanswered question": "\ub2f5\ubcc0\uc774 \uc5c6\ub294 \uc9c8\ubb38",
    "{numResponses} other response": [
      "\uae30\ud0c0 \uc751\ub2f5 {numResponses}\uac1c"
    ],
    "{numResponses} response": [
      "\uc751\ub2f5 {numResponses}\uac1c"
    ],
    "{numVotes} Vote": [
      "{numVotes}\ud45c"
    ],
    "{unread_comments_count} new": "\uc2e0\uaddc {unread_comments_count}\uac1c",
    "\u2026": "\u2026"
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
        return value[django.pluralidx(count)];
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
    "DATETIME_FORMAT": "Y\ub144 n\uc6d4 j\uc77c g:i A",
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
      "%m/%d/%y",
      "%Y\ub144 %m\uc6d4 %d\uc77c %H\uc2dc %M\ubd84 %S\ucd08",
      "%Y\ub144 %m\uc6d4 %d\uc77c %H\uc2dc %M\ubd84"
    ],
    "DATE_FORMAT": "Y\ub144 n\uc6d4 j\uc77c",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%m/%d/%Y",
      "%m/%d/%y",
      "%Y\ub144 %m\uc6d4 %d\uc77c"
    ],
    "DECIMAL_SEPARATOR": ".",
    "FIRST_DAY_OF_WEEK": "0",
    "MONTH_DAY_FORMAT": "n\uc6d4 j\uc77c",
    "NUMBER_GROUPING": "3",
    "SHORT_DATETIME_FORMAT": "Y-n-j H:i",
    "SHORT_DATE_FORMAT": "Y-n-j.",
    "THOUSAND_SEPARATOR": ",",
    "TIME_FORMAT": "A g:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M",
      "%H\uc2dc %M\ubd84 %S\ucd08",
      "%H\uc2dc %M\ubd84"
    ],
    "YEAR_MONTH_FORMAT": "Y\ub144 n\uc6d4"
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

