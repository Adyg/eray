//"use strict";

var Eray = { };

(function ( $ ) {
    /**
    * Handle tag autocomplete functionality
    *
    */
    Eray.autocomplete = function($container) {
        // parameter documentation at http://nicolasbize.com/magicsuggest/doc.html
        $container.find('input').magicSuggest({
            allowFreeEntries: false,
            data: $container.attr('rel'),
            method: 'GET',
            hideTrigger: true,
            minChars: 2
        });
    }

    /**
    * Handle Markdown editor
    *
    */
    var markdownIDE;
    Eray.markdown = function($markdownElement) {
        if($markdownElement.length) {
            markdownIDE = new SimpleMDE({ 
                element: $markdownElement[0],
                showIcons: ['code', 'table'],
                spellChecker: false,
                renderingConfig: {
                    codeSyntaxHighlighting: true
                }
            });
        }
    }

    /**
    * Handle filters on Community page
    *
    */
    Eray.communityFilter = function($filter) {
        $filter.on('change', function(e){
            var $this = $(this),
                $form = $this.parents('form:first');

            $form.submit();
        });
    }

    /**
    * Question&Comment vote up/down
    *
    */
    Eray.vote = function() {
        var $votingTriggers = $('.vote');

        $votingTriggers.on('click', function(e){
            e.preventDefault();
            var $this = $(this),
                $counter = $this.parents('.controls:first').find('.votes .count');

            $.ajax({
                url: $this.attr('href'), 
                success: function(result){
                    $counter.html(result);
                }
            });            
        });
    }

    /**
    * Tag & Question subscribe
    * 
    */
    Eray.subscribe = function() {
        var $subscribeTriggers = $('.subscribe');

        $subscribeTriggers.on('click', function(e){
            e.preventDefault();
            var $this = $(this);

            $.ajax({
                url: $this.attr('href')
            });
        });
    }

    /**
    * Handle commenting forms
    *
    */
    Eray.comments = function() {
        var toggleForms = function() {
            var $togglers = $('a.add-comment');

            $togglers.on('click', function(e){
                e.preventDefault()
                var $this = $(this),
                    $form = $this.next();

                if($this.attr('rel')) {
                    $form = $('#'+$this.attr('rel')).find('.comment-form');
                }

                $form.toggleClass('active');
            });
        }

        var commentFormSubmit = function() {
            var $commentForms = $('.comment-form form');

            $commentForms.on('submit', function(e) {
                e.preventDefault();
                var $this = $(this),
                    $commentList = $this.parents('.comment-list:first').find('ul'),
                    $textarea = $this.find('textarea'),
                    $error = $this.find('.error');

                $.ajax({
                    url: $this.attr('action'),
                    dataType: 'json',
                    method: $this.attr('method'),
                    data: $this.serialize(),
                    success: function(result){
                        if(result.success) {
                            $('<li>'+result.message+'</li>').appendTo($commentList);
                            $textarea.val('');
                            $error.html('');
                        }

                        if(result.failed) {
                            $error.html(result.message);
                        }
                    }
                });                
            });
        }

        toggleForms();
        commentFormSubmit();
    }

    /**
    * Handle search related forms
    *
    */
    Eray.search_form = function($form) {
        $form.on('submit', function(e) {
            e.preventDefault();
            var $input = $form.find('input:first');

            if($input.val()) {
                window.location.href = $form.attr('action') + $input.val();
            }
        });
    }

    Eray.initAll = function() {
        Eray.autocomplete($('.autocomplete'));
        Eray.markdown($('.markdown textarea'));
        Eray.communityFilter($('.community-filter select'));
        Eray.vote();
        Eray.subscribe();
        Eray.comments();
        Eray.search_form($('#navbar form'));
    }

    Eray.initAll();

}( jQuery ));