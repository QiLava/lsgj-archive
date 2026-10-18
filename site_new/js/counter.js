$.ajax({
	url: '/ppf/counter.php',
	type: 'POST',
	async: false,
	cache: false,
	data: "getcounter=1",
	success: function(d){
		d=eval('('+d+')');
		document.write("<span class='ct1'>总访问量：<i>"+d.allpv+"</i> </span><span class='ct2'>总浏览量：<i>"+d.alluv+"</i> </span><span class='ct3'>今日访问: <i>"+d.todaypv+"</i> </span><span class='ct4'>今日浏览: <i>"+d.todayuv+"</i> </span>");
	  }
});