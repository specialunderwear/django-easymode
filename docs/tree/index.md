tree
====

Easymode has full admin support. Since content easymode was designed to handle
is heavy hierarchic, easymode can also support this in the admin.

The single most annoying problem you will encounter when building django apps,
is that after you discovered the niceties of InlineModelAdmin, you find out it
can only support 1 level of inlines. It does not support any form of recursion.

Easymode can not make InlineModelAdmin recursive either, because that would become
a mess. What is *can* do, is display links to all related models. This way you have
them in reach where you need them. There is no need to go back to the admin and
select a different section to edit the related models. 

Easymode has the *+* button, like foreign keys allow you to add a related model 
from the change view, using the *+* button, easymode has the same for *ALL* 
related models.

The thing that is very different about easymode's *+* button is that it allows adding
objects that point *TO* the currently edited model, instead of objects that the 
currently edited model points to.