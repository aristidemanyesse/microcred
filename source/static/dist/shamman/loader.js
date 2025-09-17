
class Loader {

	static start(){
		$(".leloader").css("display", "initial");
	}

	static stop(){
		$(".leloader").css("display", "none");
	}

	static pause(){
		this.start()
		$(".leloader .loading").css("animation-play-state", "paused");
	}

}