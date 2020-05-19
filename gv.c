#include "chibi.h"
int setid =1;

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
void p_VarList( VarList *locals, int nest );
void ast_varlist( VarList *locals );
void p_Function( Function *fns, int nest );
void p_Type( Type *t, int nest );
void p_Node( Node *N, int next );

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
  printf("digraph G { \nnode {shape=record, fotname=\"Arial\"];\n");
  p_Program( prog );
  printf("}\n");
	
}

void p_Program(
Program *prog)
{
	int next = 0;
	printf("print globals\n");
	printf("set%2d [label = \"{globals|functions}\"];", setid );
	p_VarList( prog->globals, 0 );
	p_Function( prog->fns, 0 );
}

void p_Function(
Function *fns,
int nest
)
{
	Function *next;
	Node *Nnext;
	if( !fns ) return;

	PS(nest);RED; printf("p_function"); BLACK;

	next = fns;
	while( next ) {
		RED;
		printf("function name <%s>\n",next->name );
		BLACK;
		printf("is_static <%d>", next->is_static );
		PS( nest +1 )
		printf("has_varargs <%d>", next->has_varargs );
		PS( nest +1 )
		printf("stack_size <%d>\n", next->stack_size);

		MAGEN;
		printf("params\n");
		BLACK;
		p_VarList( next->params, nest+1 );
		/* VarList *params; */
		Nnext = next->node;
		while( Nnext ) {
			p_Node( Nnext, nest+1 );
			Nnext = Nnext->next;
		}
		/* VarList *locals; */
		MAGEN;
		printf("locals\n");
		BLACK;
		p_VarList( next->locals, nest+1 );
		next = next->next;
	}

}

void p_Var( Var *V, int nest ) {

	if( !V ) return;

	PS( nest );RED; printf("p_Var"); BLACK;

	YELLOW;
	printf("<name>=%s",V->name);
	BLACK;
	PS(1);
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
void p_VarList( VarList *locals, int nest )
{
	VarList *VLnext;
	VLnext = locals;

	if( !locals ) return;

	PS(nest);RED; printf("p_VarList"); BLACK;

	while( VLnext ) {
		p_Var( VLnext->var, nest );
		VLnext = VLnext->next;
	}
}
	
/*
struct VarList {
  VarList *next;
  Var *var;
}
*/


/*
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

void p_Type( Type *T, int dummy ) {

	while( T ) {
		printf("set%02d [ label = \"{<H%02d> kind|size|align|is_incomplete|array_len|base}|{%s|%d|%d|%d|%d|<B%02d>%x}\"];\n",
				setid,
				setid,
				pType(T->kind),
				T->size,
				T->align,
				T->is_incomplete,
				T->array_len,
				setid,
				T->base
				);
		if( T->base ) {
			printf("set%02d:B%02d -> set%02d:H%02d;\n",
					setid, setid, setid+1, setid+1);
		}
		setid++;
		T = T->base;
	}

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

void p_Node( Node *N, int nest ){
	if( !N ) { return; }
	PS(nest);RED; printf("p_Node\n"); BLACK;

	PS(nest);printf("<kind>=%s, %d\n",NDKIND[ N->kind ], N->kind );
//  Node  printf("<next>=%d\n",N->next);
	//p_Node( N->next,nest+1 );
//  Type  printf("<ty>=%d\n",N->ty);
	p_Type( N->ty, nest+1 );
//  Token  printf("<tok>=%d\n",N->tok);
//  Node  printf("<lhs>=%d\n",N->lhs);
    if( N->lhs ) {
		PS( nest );printf("lhs\n");
		p_Node( N->lhs, nest+1 );
	}
//  Node  printf("<rhs>=%d\n",N->rhs);
    if( N->rhs ) {
		PS( nest );printf("rhs\n");
		p_Node( N->rhs, nest+1 );
	}
//  Node  printf("<cond>=%d\n",N->cond);
//  Node  printf("<then>=%d\n",N->then);
//  Node  printf("<els>=%d\n",N->els);
//  Node  printf("<init>=%d\n",N->init);
//  Node  printf("<inc>=%d\n",N->inc);
//  Node  printf("<body>=%d\n",N->body);
//  Member  printf("<member>=%d\n",N->member);
	PS( nest ); printf("<funcname>=%s\n",N->funcname);
//  Node  printf("<args>=%d\n",N->args);
	PS( nest ); printf("<label_name>=%s\n",N->label_name);
//  Node  printf("<case_next>=%d\n",N->case_next);
//  Node  printf("<default_case>=%d\n",N->default_case);
	PS( nest ); printf("<case_label>=%d\n",N->case_label);
	PS( nest ); printf("<case_end_label>=%d\n",N->case_end_label);
//  Var  printf("<var>=%d\n",N->var);
	PS( nest ); printf("<val>=%l\n",N->val);
}
