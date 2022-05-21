$(document).ready(function() {
    $('#add').on('click', function() {
        var $very_unique = $('.very-unique');
        $very_unique.clone().appendTo('#payment-form');
    })
  });

// $(document).ready(function() {
//       $('#add').on('click', function() {
//         var field =`
//         <br><br><br>
//         <div class="form-row float-right">
//         <div class="col-auto">
//             <label class="sr-only" for="inlineFormInput">Platform</label>
//             <select name="Platform" class="btn btn-secondary" id="dropdownMenuButton" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
//                 {% for platform in platforms %}
//                     <option value="{{ platform }}">{{ platform }}</option>
//                 {% endfor %}
//             </select>
//         </div>
//         <div class="col-auto">
//             <label class="sr-only" for="inlineFormInputGroup">Username</label>
//             <div class="input-group mb-2">
//             <div class="input-group-prepend">
//                 <div class="input-group-text">@</div>
//             </div>
//                 {{ form.receivers(placeholder="example, me", type="text", class="form-control", id="inlineFormInputGroup") }}
//             </div>
//         </div>
//           <div class="col-auto">
//             <span class="btn btn-white col-md-6"></span>
//         </div>
//         <span class="btn btn-white col-md-6"></span>`;
//         $('#payment-form').append(field);
//       }); 
// });

// $(document).ready(function() {
//     $("iframe").css('background', 'white');
// });

// // $(document).ready(function() {
// //     $('#add').on('click', function() {
// //         function removeDummy() {
// //             var elem = document.getElementById('dummy');
// //             elem.parentNode.removeChild(elem);
// //             return false;
// //         }
// //     })
// // });