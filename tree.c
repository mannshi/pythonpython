#include "chibi.h"
int setid =1;
int setidType =1;
int setidVar =1;
int setidFunction =1;
int setidNode =1;


char Type_tbl0[4096] = 
"setType [ xlabel = \"TYPE\", label = \"{ADDR|kind|size|align|is_incomplete|array_len|members|return_ty|base}";
char Type_tbl[4096];

char Type_edge[4096] = "";

char Function_tbl[4096];

char VarList_tbl[4096];

char *NDKIND[] = {
"ND_ADD",
"ND_PTR_ADD",
"ND_SUB",
"ND_PTR_SUB",
"ND_PTR_DIFF",
"ND_MUL",
"ND_DIV",
"ND_BITAND",
"ND_BITOR",
"ND_BITXOR",
"ND_SHL",
"ND_SHR",
"ND_EQ",
"ND_NE",
"ND_LT",
"ND_LE",
"ND_ASSIGN",
"ND_TERNARY",
"ND_PRE_INC",
"ND_PRE_DEC",
"ND_POST_INC",
"ND_POST_DEC",
"ND_ADD_EQ",
"ND_PTR_ADD_EQ",
"ND_SUB_EQ",
"ND_PTR_SUB_EQ",
"ND_MUL_EQ",
"ND_DIV_EQ",
"ND_SHL_EQ",
"ND_SHR_EQ",
"ND_BITAND_EQ",
"ND_BITOR_EQ",
"ND_BITXOR_EQ",
"ND_COMMA",
"ND_MEMBER",
"ND_ADDR",
"ND_DEREF",
"ND_NOT",
"ND_BITNOT",
"ND_LOGAND",
"ND_LOGOR",
"ND_RETURN",
"ND_IF",
"ND_WHILE",
"ND_FOR",
"ND_DO",
"ND_SWITCH",
"ND_CASE",
"ND_BLOCK",
"ND_BREAK",
"ND_CONTINUE",
"ND_GOTO",
"ND_LABEL",
"ND_FUNCALL",
"ND_EXPR_STMT",
"ND_STMT_EXPR",
"ND_VAR",
"ND_NUM",
"ND_CAST",
"ND_NULL" };

void ast( Program * );
void p_Program( Program *p );
void p_Var( Var *v, int nest );
void p_VarList( VarList *locals, int nest, char *Fname );
void ast_varlist( VarList *locals );
void p_Function( Function *fns, int nest );
void p_Type( Type *t, int nest );
void p_Type2( Type *t, int nest );
void p_Node( Node *N, char *func );
void p_Node2( Node *N, Node *top, int parent);

#define PS(n) for(int ps=1; ps<=n; ps++ ) printf("|");
#define pType(t) ( t == TY_VOID ?  "TY_VOID" : ( t == TY_BOOL ?  "TY_BOOL" : ( t == TY_CHAR ?  "TY_CHAR" : ( t == TY_SHORT ?  "TY_SHORT" : ( t == TY_INT ?  "TY_INT" : ( t == TY_LONG ?  "TY_LONG" : ( t == TY_ENUM ?  "TY_ENUM" : ( t == TY_PTR ?  "TY_PTR" : ( t == TY_ARRAY ?  "TY_ARRAY" : ( t == TY_STRUCT ?  "TY_STRUCT" : ( t == TY_FUNC ?  "TY_FUNC" : "TYP_ERROR" )))))))))))

#define YELLOW printf("\x1b[33m")
#define BLACK  printf("\x1b[0m")
#define RED    printf("\x1b[31m")
#define MAGEN  printf("\x1b[35m")
/*
struct Function {
  Function *next;
  char *name;
  VarList *params;
  bool is_static;
  bool has_varargs;

  Node *node;
  VarList *locals;
  int stack_size;
};
*/

/*
typedef struct {
  VarList *globals;
  Function *fns;
} Program;
*/

void ast( Program *prog ) {
  // VarList *globals;
  //
  // Function *fns;
  printf("digraph G { \n");
	printf("node [shape=record, fotname=\"Arial\"];\n");
	printf("graph [ rankdir = TB ];\n");

  p_Program( prog );

  printf("}\n");
	
}

void p_Program(
Program *prog)
{
	int next = 0;
	//printf("print globals\n");
	strcpy( Type_tbl, Type_tbl0 );
	printf("set%02d [label = \"{globals|functions}\"];\n", setid );

	p_VarList( prog->globals, 0, "globals" );


	p_Function( prog->fns, 0 );
	strcat( Type_tbl, "\"];\n" );
	printf("%s\n", Type_tbl );
	printf("%s\n", Type_edge );

}

void p_Function(
Function *fns,
int nest
)
{
	char tmp[1024];
	Function *next;
	Function *F;
	Node *Nnext;

	if( !fns ) return;


	printf("setFunction%02d [ xlabel=\"Function\"label = \"{name|params|is_static|has_varargs|node|locals|stack_size}", setidFunction );
	F = fns;
	// 関数毎のループ
	while( F != NULL ) {
		printf( "|{%s|%x|%d|%d|%x|%x|%d}",
				F->name,
				F->params,
				F->is_static,
				F->has_varargs,
				F->node,
				F->locals,
				F->stack_size );

/*
struct Function {
  Function *next;
  char *name;
  VarList *params;
  bool is_static;
  bool has_varargs;

  Node *node;
  VarList *locals;
  int stack_size;
};
*/

		//p_VarList( F->params, 0, F->name );

		F = F->next;

	}
	// 関数毎のループ 終わり
	strcat( Function_tbl, tmp );

	setidFunction++;
	printf(" \"];\n");

	F = fns;
	// 関数毎のループ パラメータ
	while( F != NULL ) {
		p_VarList( F->params, 0, F->name );
		F = F->next;
	}

	F = fns;
	// 関数毎のループ ローカル変数
	while( F != NULL ) {
		p_VarList( F->locals, 0, F->name );
		F = F->next;
	}

	F = fns;
	// 関数毎のループ node
	while( F != NULL ) {
		p_Node( F->node, F->name  );
		F = F->next;
	}

	return;
}

void p_Var( Var *V, int nest ) {

	if( !V ) return;

	printf("<name>=%s",V->name);
	printf(" <is_local>=%d",V->is_local); PS(1);
	printf(" <offset>=%d",V->offset); PS(1);
	printf(" <is_static>=%d",V->is_static); printf("\n");
	p_Type( V->ty, nest + 1 );
	//printf("<initializer>=%d\n",V->initializer);
}
/*
struct Var {
  char *name;    // Variable name
  Type *ty;      // Type
  bool is_local; // local or global

  // Local variable
  int offset;    // Offset from RBP

  // Global variable
  bool is_static;
  Initializer *initializer;
};
*/
void p_VarList( VarList *locals, int nest, char *Fname )
{
	Var *v;
	char buff[1024];

	if( !locals ) return;

	printf("setVar%s [ xlabel = \"%s\"label = \"{name|ty|is_local|offset|is_static|initializer}", Fname);
	while( locals ) {
		v = locals->var;
		printf( "|{%s|<%x> %x|%d|%d|%d|%x}",
				v->name, v->ty, v->ty, v->is_local, v->offset, v->is_static, v->initializer );

		// edge 
		
		p_Type( v->ty, 0 );
		locals = locals->next;
	}
	setidVar++;
	printf(" \"];\n");
}

	
/*
struct VarList {
  VarList *next;
  Var *var;
}
*/



void p_Type( Type *T, int dummy ) {

	char tmp[1024];

	while( T ) {
		sprintf( tmp,
				"|{<TO%x>%x|%s|%d|%d|%d|%d|%x|%x|<FROM%x> %x}",
				T, T,
				pType(T->kind),
				T->size,
				T->align,
				T->is_incomplete,
				T->array_len,
				T->members,
				T->return_ty,
				T->base,
				T->base
				);
		strcat( Type_tbl, tmp );

/*
		if( T->base ) {
			char tmp[1024];
			sprintf(tmp, "setType:FROM%x -> setType:TO%x;\n",
					T->base, T->base);
			strcat( Type_edge, tmp );
		}
*/

		//setidType++;
		T = T->base;
	}

}

void p_Type2( Type *T, int dummy ) {

	char Type_tbl2[4096] = 
	"setType%x [ xlabel = \"TYPE\", label = \"{ADDR|kind|size|align|is_incomplete|array_len|members|return_ty|base}";

	char tmp[1024];

	if( !T ) return;

	sprintf( Type_tbl2,
			"setType%x [ xlabel = \"TYPE\", label = \"{ADDR|kind|size|align|is_incomplete|array_len|members|return_ty|base}",
			T );

	while( T ) {
		sprintf( tmp,
				"|{<TO%x>%x|%s|%d|%d|%d|%d|%x|%x|<FROM%x> %x}",
				T, T,
				pType(T->kind),
				T->size,
				T->align,
				T->is_incomplete,
				T->array_len,
				T->members,
				T->return_ty,
				T->base,
				T->base
				);
		strcat( Type_tbl2, tmp );

		T = T->base;
	}

	strcat( Type_tbl2, "\"];\n" );
	printf("%s", Type_tbl2 );

}

/*
struct Type {
  TypeKind kind;
  int size;           // sizeof() value
  int align;          // alignment
  bool is_incomplete; // incomplete type

  Type *base;         // pointer or array
  int array_len;      // array
  Member *members;    // struct
  Type *return_ty;    // function
};
*/

void p_Node( Node *N, char *func ){

	char Node_tbl[4096];
	char tmp[1024];


	while( N ) {
		p_Node2( N, N, 0 );
		//strcat( Node_tbl, tmp );
				
		N = N->next;
	}
	
	//strcat( Node_tbl, "\"];\n" );

	printf(Node_tbl);
}


void p_Node2( Node *N, Node *top, int parent ){
	int myid;

	if( !N ) return;

		printf( "Node_%02d [ colorscheme=\"rdylgn11\", color=7,  xlabel = \"%s_node\" label=\"{top|ADDR|kind|ty|tok|lhs|rhs|var|val}",
				setidNode, "tmp" );


	printf(
		 "|{%x|%x|%s|%x|%x|%x|%x|%x|%ld}",
		top,
		N,
		NDKIND[N->kind],
		N->ty,
		N->tok,
		N->lhs,
		N->rhs,
		N->var,
		N->val
		);
	printf( "\"];\n" );
	myid = setidNode++;


	p_Type2( N->ty, 1 );
	if( N->ty )
		printf("Node_%02d -> setType%x [style = dotted];\n",
				setidNode-1, N->ty );

	if( parent != 0 ) {
		printf( "Node_%02d->Node_%02d;\n", parent, myid );
	}


	p_Node2( N->lhs, top, myid );
	p_Node2( N->rhs, top, parent+1 );
	p_Node2( N->cond, top, parent+1 );
	p_Node2( N->then, top, parent+1 );
	p_Node2( N->els, top, parent+1 );
	p_Node2( N->init, top, parent+1 );
	p_Node2( N->inc, top, parent+1 );
	p_Node2( N->body, top, parent+1 );
	p_Node2( N->args, top, parent+1 );
	p_Node2( N->case_next, top, parent+1 );
	p_Node2( N->default_case, top, parent+1 );
	/**/
}
/*
 *
struct Node {
  NodeKind kind; // Node kind
  Node *next;    // Next node
  Type *ty;      // Type, e.g. int or pointer to int
  Token *tok;    // Representative token

  Node *lhs;     // Left-hand side
  Node *rhs;     // Right-hand side

  // "if, "while" or "for" statement
  Node *cond;
  Node *then;
  Node *els;
  Node *init;
  Node *inc;

  // Block or statement expression
  Node *body;

  // Struct member access
  Member *member;

  // Function call
  char *funcname;
  Node *args;

  // Goto or labeled statement
  char *label_name;

  // Switch-cases
  Node *case_next;
  Node *default_case;
  int case_label;
  int case_end_label;

  // Variable
  Var *var;

  // Integer literal
  long val;
};
*/
