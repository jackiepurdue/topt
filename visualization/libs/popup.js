(function($) {
    $.fn.extend({
        popup: function(options) {
            // accept an options object with sensible defaults
            var defaults = {
                scrollbars:			false,
                resizable:			false,
                status:				false,
                width:				800,
                height:				600
            };
            var options = $.extend(defaults, options);
			options.resizable = (options.resizable) ? 'yes' : 'no';
			options.status = (options.status) ? 'yes' : 'no';
			options.scrollbars = (options.scrollbars) ? 'yes' : 'no';

            return this.each(function() {
                $(this).click( function(e) {
                	e.preventDefault();
                	pop($(this).attr('href'), $(this).html(), options.width, options.height, options.scrollbars);
                });
            });

            function pop(url, winName, wWidth, wHeight, scrll)
			{
				var scrollB;
			   if(!scrll)
			   {
			      scrollB = 'no';
			      var pWidth = wWidth;
			      var rSize = 'no';
			   }
			   else
			   {
			      scrollB = scrll;
			      wWidth = parseInt(wWidth) + 20;
			      var rSize = 'yes';
			   }
			   var iMyWidth;
			   var iMyHeight;
			   iMyWidth =(window.screen.width / 2) - (wWidth / 2 + 10);
			   //half the screen width minus half the new window width (plus 5 pixel borders).
			   iMyHeight =(window.screen.height /2) - (wHeight / 2 + 15);
			   //half the screen height minus half the new window height (plus title and status bars).
			   var zWin = window.open(url, winName, "status=no,width=" + wWidth + ",height=" + wHeight + ",resizable=" + rSize + ",left=" + iMyWidth + ",top=" + iMyHeight + ",screenX=" + iMyWidth + ",screenY=" + iMyHeight + ",scrollbars=" + scrollB);
			   zWin.focus();
			}
        }
    });
}) (jQuery);