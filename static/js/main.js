//fetch students
$(document).ready(function(){
   $('span#ajaxloader').hide();
   $('span#nomore').hide();
$("#fetchHotels").click(function(){
   $('span#ajaxloader').show();
   var city = $("#city").val();
   var page = $('input#ajaxpage').val();
  
   var dataString = 'city=' + city + '&page=' + page;
   $.ajax({
             type: "POST",
             url: "/fetchmorehotels",
            data: dataString,
            cache: false,
            async: true,
            success: function(result){          
            
                    var position=result.indexOf("||");
                    var warningMessage=result.substring(0,position);
                    if(warningMessage=='error'){
                      var errorMessage=result.substring(position+2);                       
                    }else {
                      if(result.trim()=='-1'){
                        // $('span#nomore').show();
                        // $("span#nomore").html("No more hotels found");
                      }else{
                        $("#fetchedData").append(result);
                        $('input#ajaxpage').val(page+1); 
                      }                       
                    }  
                    $('span#ajaxloader').hide();          
      }
  });
});
});

//submit review and show
$(document).ready(function(){
   $('span#ajaxloader').hide();
   $("#review_submit_button").click(function(){
   $('span#ajaxloader').show();

   var hid = $('input#hotel_id').val();
   var review = $('#text').val();
   if(review.length <=10){
    $('span#ajaxloader').hide();
    return;
   }
   // alert(review);
   var dataString = 'hid=' + hid + '&review=' + review;
   $.ajax({
             type: "POST",
             url: "/submitreview",
            data: dataString,
            cache: false,
            async: true,
            success: function(result){          
            
                    var position=result.indexOf("||");
                    var warningMessage=result.substring(0,position);
                    if(warningMessage=='error'){
                      var errorMessage=result.substring(position+2);                       
                    }else {
                      if(result.trim()=='-1'){
                        // $('span#nomore').show();
                        // $("span#nomore").html("No more hotels found");
                      }else{
                        $('#text').val('');
                        $("#reviews_list_div").html(result);
                      }                       
                    }  
                    $('span#ajaxloader').hide();          
      }
  });
});
    $('span#ajaxloader').hide();
});