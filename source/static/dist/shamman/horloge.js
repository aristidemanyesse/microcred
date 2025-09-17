
$(function(){

	    //Format date
	    formatDate = function(ladate){
	    	if (ladate == null) {
	    		ladate = new Date(ladate);
	    	}
	    	if (moment(ladate).isValid()) {
	    		val = moment(ladate);
	    		newdate = val.year()+"-"+concate0(val.month()+1)+"-"+concate0(val.date())+" "+concate0(val.hour())+":"+concate0(val.minute())+":"+concate0(val.second());
	    		return newdate;
	    	}else{
	    		return ladate = new Date();
	    	}
	    }

		concate0 = function(nom){
			if (nom < 10) {
				return "0"+nom;
			}else{
				return nom;
			}
		}

	    horloge = function(){
	    	tabMois = ["Janvier", "Février", "Mars","Avril","Mai","Juin", "Juillet", "Août","Septembre","Octobre","Novembre", "Décembre"];
	    	tabSemaine = ["Dimanche", "Lundi", "Mardi", "Mercredi","jeudi","Vendredi","Samedi"];

	    	ladate = new Date();
	    	j = ladate.getDay();
	    	jj = concate0(ladate.getDate());
	    	MM = concate0(ladate.getMonth());
	    	yy = ladate.getFullYear();
	    	hh = concate0(ladate.getHours());
	    	mm = concate0(ladate.getMinutes());
	    	ss = concate0(ladate.getSeconds());

	    	jour = tabSemaine[parseInt(j)];
	    	MM = tabMois[parseInt(MM)];

	    	$("#heure_actu").html(hh+':'+mm+':'+ss)
	    	$("#date_actu").html(jour+' '+jj+' '+MM+' '+yy)
	    }

	    setInterval(function(){
	    	horloge();
	    }, 1000);


	})