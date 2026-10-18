/*****此处可以加入自定义的一些javascript代码*******/
/*如果在新的模板中修改，只需要拷贝修改的内容 */
function secBoards1(n)
{
for(i=0;i<menu_h.childNodes.length;i++)
menu_h.childNodes[i].className="sec7";
menu_h.childNodes[n].className="sec8";
for(i=0;i<main_h.childNodes.length;i++)
main_h.childNodes[i].style.display="none";
main_h.childNodes[n].style.display="block";
}
function secBoards(n)
{
for(i=0;i<menu2.childNodes.length;i++)
menu2.childNodes[i].className="sec5";
menu2.childNodes[n].className="sec6";
for(i=0;i<main2.childNodes.length;i++)
main2.childNodes[i].style.display="none";
main2.childNodes[n].style.display="block";
}