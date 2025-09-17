
class Alerter {

	static success(title, message){
		Loader.stop();
		toastr.options = {
			closeButton: true,
			progressBar: true,
			showMethod: 'slideDown',
			timeOut: 3000
		};
		toastr.success(message, title);
	}

	static warning(title, message){
		toastr.options = {
			closeButton: true,
			progressBar: true,
			showMethod: 'slideDown',
			timeOut: 3000
		};
		toastr.warning(message, title);
	}


	static error(title, message){
		Loader.stop();
		toastr.options = {
			closeButton: true,
			progressBar: true,
			showMethod: 'slideDown',
			timeOut: 3000
		};
		toastr.error(message, title);
	}

}