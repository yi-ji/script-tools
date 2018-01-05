var username = 'your username';
var query_url = 'https://bbs.pku.edu.cn/v2/search.php?mode=post&bid=0&owner='+username+'&days=24855' // add '&page=1,2,...' if undeletable posts block search result page
var post_num = 3025; // just estimated

function sleep(ms){
   var start = new Date().getTime();
   var end = start;
   while(end < start + ms) {
     end = new Date().getTime();
  }
}

function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}
// post('/v2/ajax/operate_post.php', {bid: '176', list: '[12084385]', action: 'delete'});

async function main()
{
    for (var num = 0; num < post_num; num += 21)
    {
        var query_page = document.createElement('iframe');
        query_page.src = query_url;
        var process_page = new Promise(resolve => {
            query_page.onload = async function() {
                var all_post_div = query_page.contentDocument.querySelectorAll('div.text-line-limit');
                for (post_idx in all_post_div)
                {
                    try
                    {
                        var post_url = all_post_div[post_idx].children[0].href;
                        console.log(post_url);
                        if (post_url.includes('threadid=16274659'))
                        {
                            continue;
                        }
                        var post_page = document.createElement('iframe');
                        post_page.src = post_url;
                        post_page.width = screen.width;
                        post_page.height = screen.height;
                        var process_post = new Promise(resolve => {
                            post_page.onload = function() {
                                var del_post = post_page.contentDocument.querySelector('[data-action="delete-post"]');
                                console.log(del_post);
                                try
                                {
                                    del_post.click();
                                }
                                catch(err)
                                {
                                    resolve();
                                }
                                sleep(1500);
                                var del_post_confirm = post_page.contentDocument.querySelector('[data-action="bdwm-confirm-dialog-yes"]');
                                console.log(del_post_confirm);
                                del_post_confirm.click();
                                sleep(1500);
                                console.log('post deleted');
                                resolve();
                            };
                            document.body.insertAdjacentElement('afterbegin', post_page);
                        });
                        await process_post;
                        document.body.removeChild(post_page);
                    }
                    catch(err)
                    {
                        continue;
                    }
                }
                resolve();
            };
            document.body.appendChild(query_page);
        });
        await process_page;
        document.body.removeChild(query_page);
    }
}

main();