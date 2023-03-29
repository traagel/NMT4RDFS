# How I think this code works


# 1. start from create_lubm_graph_words.sh
1) Unzip graphs_with_descriptions.zip
1) Unzip jena_inference_with_descriptions.zip
1) Run prepare_lubm_data.py


# 2. Prepare_lubm_data.py
## 1) encode_lubm_dataset()
1) Try reading from pickle
1) If fails - Create encoding
   1) get_lubm_classes()
   2) get_lubm_properties()
   3) get_lubm_properties_groups (_subProperty of imported properties_)
1) **These functions read data from either:**
   1) Local GraphQL instance
   2) Local files:
      1) /data/lubm1_intact/encoding/lubm_classes.pz
      2) /data/lubm1_intact/encoding/properties.pz
      3) /data/lubm1_intact/encoding/properties_groups.pz
1) Create a GraphWordsEncoder class
2) **Create lubm files dataframe (get_lubm_files_df())**

Code using real paths as example:

```python
def get_lubm_files_df():
    logging.info("Creating dataframe for LUBM1 input/inference pairs")
    rdf_files = []
    for input_graph_path in tqdm(sorted(glob("../data/lubm1_intact/graphs_with_descriptions/" + "*"))):
        input_graph_file = os.path.basename(input_graph_path)
        inference_path = "../data/lubm1_intact/jena_inference_with_descriptions/" + input_graph_file
        graph_type = get_lubm_graph_type(input_graph_path)
        rdf_pair = {"input_graph_file": input_graph_path, "inference_file": inference_path, "graph_type": graph_type}
        rdf_files.append(rdf_pair)
    files_df = pd.DataFrame.from_dict(rdf_files)
    return files_df
```
## 2.5 Dataframe creation

### 2.5.1) Get the input graphs from path (hardcoded)

### 2.5.2) Get the graph with inference (Jena inference engine)

### 2.5.3) Get the type from the name 
For example:
```
"C:/Users/martt/PycharmProjects/NMT4RDFS/data/lubm1_intact/graphs_with_descriptions/HTTP_www.Department0.University0.edu_AssistantProfessor0.nt"
```

Returns "AssistantProfessor"

### 2.5.4) Create a dictionary -> dataframe (input_graph_path, inference_graph_path, graph_type)


## 2.6) Encode the dataframe
### 1) encode_graphs_list(lubm_graph_words_encoder, lubm_files_df, "nt")
1) Input is the graph_words_encoder CLASS, the dataframe with files, rdf format
1) Create 3 empty lists, for graph encodings, inference encodings, resources dictionaries
1) FOR LOOP the files DF
   1) **encode_input_graph(graph_words_encoder, row, rdf_format)**
    
    
**How does it encode?**

Graph() -> parse input file to Graph() class

graph_words_encoder.encode_graph(input_graph) 

(read file from path, turn into "graph" object)

## graph_words_encoder.encode_graph(input_graph)

encode_graphs_list ->  encode_input_graph(Encoder class) -> encode_input_graph(encoder class) -> graph_words_encoder.encode_graph()

1. If property not in TBOX -> remove triple
2. If skip blank nodes (default) & blank node -> remove triple
3. If skip type "resource" & object == RDFS.Resource -> remove triple
4. if skip type "class" & object == RDFS.Class -> remove triple
5. if inference and object in class_resources -> add to active_classes
6. if not inference:
   1. add resource to local resources (subject, property)
   1. add resource to local resources (object, property)
9. if `verbose` (default False) -> print sub prop obj
10. active_properties add prop
11. `prop_id = active_properties[property]`
12. subj, obj <- self.resource_to_id
13. if property_id not in encoding:
14. `encoding[property_id] = []`
15. `encoding[property_id].append((subject_id, object_id))`
 
   2) encode_inference_graph(graph_words_encoder, row, resources_dictionary, rdf_format)
   3) `input_graphs_encodings.append(input_graph_encoding)`
   4) `inference_graphs_encodings.append(inference_graph_encoding)`
   5) resources_dictionaries <- resources_dictionary
   6) Add all that to files_df and return the df


---

7) Pickle it
8) Serialize it
9) serialize(lubm_graph_words_encoder, LUBM_ENCODING_DIRECTORY + GRAPH_WORDS_ENCODER)
10) return lubm_files_df, lubm_graph_words_encoder
### 2) Create Graph words
1) create_lubm_graph_words(lubm_dataset, lubm_graph_words_encoder)