"""
Contains tools to enable preview of drafts.
"""
from lxml import etree
from reversion.models import Revision
from copy import deepcopy
from easymode.tree.serializers import RecursiveXmlSerializer


__all__ = ('filter_unpublished', 'insert_draft')

class RevisionTree(object):
    """
    This class builds an xml tree from a revision, just
    like :class:`~easymode.tree.serializers.RecursiveXmlSerializer` does
    from a regular model.
    
    :attr topnode: The main node in the revision, with all child nodes nested inside.
    :attr nodelist: All nodes in the revision in a flat list.
    :meth xpath_for_node: Return an xpath statement which can be used to look
        in another xml document for the same node.
    """
    
    def __init__(self, revision_id):
        nodelist = []

        revision = Revision.objects.get(pk=revision_id)
        serializer = RecursiveXmlSerializer()
        
        # turn all version objects into lxml elements
        for ver in revision.version_set.all():
            model_instance = ver.get_object_version().object
            draft_xml = serializer.serialize([model_instance])
            draft_doc = etree.fromstring(draft_xml)
            draft_nodes = draft_doc.xpath(r'/django-objects/object')
            nodelist += draft_nodes
        
        topnode = self._find_topnode(nodelist)
        nodelist.remove(topnode)

        self.nodelist = nodelist
        # create xml topnode with nested items
        self._append_children(topnode, nodelist)
        self.topnode = topnode

    def xpath_for_node(self, node):
        return r"//object[@pk='%(pk)s' and @model='%(model)s']" \
            % {
            'pk': node.get('pk'),
            'model': node.get('model'),
        }
        
    def _get_items_by_model_and_pk(self,nodelist, model, pk):
        object_filter = lambda x: x.get('model') == model and x.get('pk') == pk
        return filter(object_filter, nodelist)

    def _get_relations(self, node):
        return map(lambda x: (x.get('to'), x.text), 
            node.xpath(r"field[@to and text() != 'None']"))

    def _get_parents(self, node, nodelist):
        result = []
        for (model, pk) in self._get_relations(node):
            result += self._get_items_by_model_and_pk(nodelist, model, pk)
        
        return result

    def _get_children(self, node, nodelist):
        children = []
        pk = node.get('pk')
        model = node.get('model')
        
        return [childnode for childnode in nodelist if \
            (model, pk) in self._get_relations(childnode)]

    def _find_topnode(self, nodelist):
        for node in nodelist:
            parents = self._get_parents(node, nodelist)
            if len(parents) == 0:
                return node
            else:
                return self._find_topnode(parents)
                
        return None

    def _append_children(self, node, nodelist):
        for child in self._get_children(node, nodelist):
            self._append_children(child, nodelist)
            node.append(child)


def insert_draft(revision_id, xml):
    """
    Insert the data belonging to revision revision_id into the xml
    
    :param revision_id: The id of the :class:`~reversion.models.Revision` we want to include.
    :param xml: A string that can be parsed as valid xml.
    :result: An xml string with the revision data included.
    """
    
    revision_tree = RevisionTree(revision_id)
    xml_doc = etree.fromstring(xml)
    
    # each separated versioned object should be replaced separately, because
    # for example list_editable view changes have many unrelated objects in 
    # a single revision
    for draft_node in revision_tree.nodelist:
        for matching_node in xml_doc.xpath(revision_tree.xpath_for_node(draft_node)):
            matching_node.getparent().replace(matching_node, deepcopy(draft_node))
    
    # when the revision is normal and not from a list_editable view, there is one
    # top node and the rest are related items. Create a tree structure with all
    # the related items as a tree, like easymode's recursive xml serializer does
    # as well.
    top_node = revision_tree.topnode
    
    for matching_node in xml_doc.xpath(revision_tree.xpath_for_node(top_node)):
        matching_node.getparent().replace(matching_node, deepcopy(top_node))
    
    return etree.tostring(xml_doc)


def filter_unpublished(xml):
    """
    Filter all unpublished objects from the xml.
    
    >>> a = '''<root>
    ... <object><field name="published">False</field>hahaha</object>
    ... <object><field name="published">True</field>hihih</object>
    ... <object><field name="koe">False</field>lololol</object>
    ... <object>
    ...     <field name="published">False</field>
    ...     hahaha
    ...     <object><field name="koe">False</field>doe eens niet</object>
    ... </object></root>'''
    >>>
    >>> filter_unpublished(a)
    '<root>\\n<object><field name="published">True</field>hihih</object>\\n<object><field name="koe">False</field>lololol</object>\\n</root>'
    
    :param xml: A string that can be parsed as valid xml.
    :result: An xml string with only published models.
    """

    select_unpublished = r"//object[field[@name='published' and text() = 'False']]"
    xml_tree = etree.fromstring(xml)
    for node in xml_tree.xpath(select_unpublished):
        node.getparent().remove(node)

    return etree.tostring(xml_tree)