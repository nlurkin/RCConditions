$(function(){
	$('.dragbox')
	.each(function(){
		$(this).find('h2').hover(function(){
			$(this).find('.configure').css('visibility', 'visible');
		}, function(){
			$(this).find('.configure').css('visibility', 'hidden');
		})
		$(this).find('.collapsep').click(function(){
			$(this).siblings('.dragbox-content').toggle();
			$(this).siblings('.collapsem').show();
			$(this).hide();
		})
		$(this).find('.collapsem').click(function(){
			$(this).siblings('.dragbox-content').toggle();
			$(this).siblings('.collapsep').show();
			$(this).hide();
		})
		.end()
		.find('.configure').css('visibility', 'hidden');
	});
	$('.column').sortable({
		connectWith: '.column',
		handle: 'h2',
		cursor: 'move',
		placeholder: 'placeholder',
		forcePlaceholderSize: true,
		opacity: 0.4,
		stop: function(event, ui){
			$(ui.item).find('h2').click();
			var sortorder='';
			$('.column').each(function(){
				var itemorder=$(this).sortable('toArray');
				var columnId=$(this).attr('id');
				sortorder+=columnId+'='+itemorder.toString()+'&';
			});
		}
	})
	.disableSelection();
});