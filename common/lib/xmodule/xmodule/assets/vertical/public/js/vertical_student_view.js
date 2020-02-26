// /* JavaScript for Vertical Student View. */
//
// /* global Set:false */ // false means do not assign to Set
//
// // The vertical marks blocks complete if they are completable by viewing.  The
// // global variable SEEN_COMPLETABLES tracks blocks between separate loads of
// // the same vertical (when a learner goes from one tab to the next, and then
// // navigates back within a given sequential) to protect against duplicate calls
// // to the server.
//
// import BookmarkButton from 'course_bookmarks/js/views/bookmark_button';
// import {markBlocksCompletedOnViewIfNeeded} from '../../../../../../../../lms/static/completion/js/CompletionOnViewService.js';
//
// var SEEN_COMPLETABLES = new Set();
//
// window.VerticalStudentView = function(runtime, element) {
//     'use strict';
//     var $element = $(element);
//     var $bookmarkButtonElement = $element.find('.bookmark-button');
//     markBlocksCompletedOnViewIfNeeded(runtime, element);
//     return new BookmarkButton({
//         el: $bookmarkButtonElement,
//         bookmarkId: $bookmarkButtonElement.data('bookmarkId'),
//         usageId: $element.data('usageId'),
//         bookmarked: $element.parent('#seq_content').data('bookmarked'),
//         apiUrl: $bookmarkButtonElement.data('bookmarksApiUrl')
//     });
// };

/* JavaScript for Vertical Student View. */
/* global markBlocksCompletedOnViewIfNeeded:false */

// TODO: IRONWOOD - need to add RequireJS to make below work and remove commented code.

window.VerticalStudentView = function(runtime, element) {
    'use strict';
    markBlocksCompletedOnViewIfNeeded(runtime, element);

    if (typeof RequireJS === 'undefined') {
        // eslint-disable-next-line no-console
        console.warn('Cannot initialize bookmarks for VerticalStudentView. RequireJS is not defined.');
        return;
    }
    RequireJS.require(['js/bookmarks/views/bookmark_button'], function(BookmarkButton) {
        var $element = $(element);
        var $bookmarkButtonElement = $element.find('.bookmark-button');

        return new BookmarkButton({
            el: $bookmarkButtonElement,
            bookmarkId: $bookmarkButtonElement.data('bookmarkId'),
            usageId: $element.data('usageId'),
            bookmarked: $element.parent('#seq_content').data('bookmarked'),
            apiUrl: $bookmarkButtonElement.data('bookmarksApiUrl')
        });
    });
};
