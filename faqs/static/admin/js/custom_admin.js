(function($) {
    $(document).ready(function() {
        // Add tooltips to translation status indicators
        $('.field-translation_status span').each(function() {
            $(this).tooltip();
        });

        // Add confirmation for bulk actions
        $('select[name="action"]').change(function() {
            var selected = $(this).val();
            if (selected === 'update_translations') {
                if (!confirm('Are you sure you want to update translations for all selected FAQs?')) {
                    $(this).val('');
                }
            } else if (selected === 'toggle_active_status') {
                if (!confirm('Are you sure you want to toggle the active status for all selected FAQs?')) {
                    $(this).val('');
                }
            }
        });

        // Auto-expand translation section if there are errors
        if ($('.field-question_hi .errors, .field-answer_hi .errors, ' +
            '.field-question_bn .errors, .field-answer_bn .errors').length) {
            $('.field-question_hi, .field-answer_hi, ' +
            '.field-question_bn, .field-answer_bn').closest('.collapse').removeClass('collapsed');
        }

        // Add warning when leaving page with unsaved changes
        var formModified = false;
        $('#faq_form :input').change(function() {
            formModified = true;
        });

        window.onbeforeunload = function() {
            if (formModified) {
                return 'You have unsaved changes. Are you sure you want to leave?';
            }
        };

        // Clear warning when submitting form
        $('form').submit(function() {
            formModified = false;
        });

        // Add keyboard shortcuts
        $(document).keydown(function(e) {
            // Ctrl/Cmd + S to save
            if ((e.ctrlKey || e.metaKey) && e.keyCode === 83) {
                e.preventDefault();
                $('input[name="_save"]').click();
            }
            // Ctrl/Cmd + Shift + T to translate
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.keyCode === 84) {
                e.preventDefault();
                if ($('input[name="auto_translate"]').is(':checked')) {
                    if (confirm('Update translations now?')) {
                        // Trigger translation update
                        $('form').append('<input type="hidden" name="_update_translations" value="1">');
                        $('form').submit();
                    }
                }
            }
        });

        // Add character counter for question fields
        $('textarea[id$="question"]').each(function() {
            var max = 200;
            var counter = $('<div class="char-counter">' + 
                          $(this).val().length + '/' + max + ' characters</div>');
            $(this).after(counter);
            
            $(this).on('input', function() {
                var count = $(this).val().length;
                counter.text(count + '/' + max + ' characters');
                if (count > max) {
                    counter.css('color', 'red');
                } else {
                    counter.css('color', '');
                }
            });
        });

        // Add preview toggle for answer fields
        $('.field-answer, .field-answer_hi, .field-answer_bn').each(function() {
            var field = $(this);
            var previewBtn = $('<button type="button" class="preview-toggle">Toggle Preview</button>');
            var preview = $('<div class="answer-preview" style="display: none;"></div>');
            
            field.append(previewBtn);
            field.append(preview);
            
            previewBtn.click(function(e) {
                e.preventDefault();
                var content = field.find('.django-quill-widget-content').html();
                preview.html(content).toggle();
            });
        });
    });
})(django.jQuery); 