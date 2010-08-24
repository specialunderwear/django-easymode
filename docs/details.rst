.. _solipsism:

Why does easymode exist?
========================

Easymode is an aspect oriented toolkit that helps making xml based flash websites easy.

The tools easymode provides are centered around the concept of hierarchy.
The basic structure of a flash frontend is hierarchical, because of
the hierarchical nature of the display list. The data that feeds such a frontend,
then will become hierarchical very quickly, should a site need to be mostly dynamic.

To enable a fully dynamic flash website, the technology used should support:

1. Rapid creation/modification of data structures.
2. A mechanism to organise these data structures in a hierarchy.
3. Enable administration of these data structures with minimal effort.
4. Enable transportation of all the information in such a hierarchical
   data set to a flash frontend.

When sites need to be internationalized, a fifth requirement forms:

5. Individual components of a hierarchy should be internationalized.

The last statement says *individual components* because the entire hierarchy
need not change amongst different localizations, only the components in the
hierarchy.

Django provides requirement 1,2 and 3:

1. Django models are the data structures, they are compact and are easily changed.
2. Foreign keys can be used as a child parent relation to create a hierarchy.
3. The django admin enables administration of models with minimal effort.

Easymode provides requirement 4 and 5:

4. An entire hierarchy of django models can be turned into xml by easymode and 
   transformed using xslt (:ref:`auto_xml`).
5. Easymode provides full internationalization of models, integrated into the django admin with support
   for hierarchical data (:ref:`internationalization_of_models`, :ref:`localization_of_admin`, :ref:`tree_explanation`).

Ofcoure, easymode also streamlines some of the things django provides, by integrating models,
hierarchy by foreign key relations and admin support.

The benefits of using django with easymode to create flash backends are:

1. A sane database, which can also feed a different frontend.
2. Easy maintenance because of simplicity of django models.
3. Code can be reused easily, because of modularity of django apps.
4. Data transport layer can be very simple because of the functional
   nature of xslt, which fits hierarchical data perfectly. (Can also be reused very easy)
5. Because the data is transported as xml, flash developers can start
   development using static xml before the backend is finished.
6. Actual mechanism to translate the content from one language to another 
   (:ref:`translation_of_contents`)
7. Structure is uniform in all layers of the application. (backend, transport, frontend)
