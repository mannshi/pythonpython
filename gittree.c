#include "chibi.h"

void ast( Program * );
void p_Program( Program *p );
void p_Var( Var *v, int nest );
void p_VarList( VarList *locals, int nest );
void ast_varlist( VarList *locals );
void p_Function( Function *fns, int nest );
void p_Type( Type *t, int nest );

#define PS(n) for(int ps=1; ps<=n; ps++ ) printf(" ");
#define pType(t) ( t == TY_VOID ?  "TY_VOID" : ( t == TY_BOOL ?  "TY_BOOL" : ( t == TY_CHAR ?  "TY_CHAR" : ( t == TY_SHORT ?  "TY_SHORT" : ( t == TY_INT ?  "TY_INT" : ( t == TY_LONG ?  "TY_LONG" : ( t == TY_ENUM ?  "TY_ENUM" : ( t == TY_PTR ?  "TY_PTR" : ( t == TY_ARRAY ?  "TY_ARRAY" : ( t == TY_STRUCT ?  "TY_STRUCT" : ( t == TY_FUNC ?  "TY_FUNC" : "TYP_ERROR" )))))))))))

#define YELLOW printf("\x1b[33m")
#define BLACK  printf("\x1b[0m")
#define RED    printf("\x1b[31m")

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
  p_Program( prog );
	
}

void p_Program(
Program *prog)
{
	int next = 0;
	YELLOW;
	printf("print globals\n");
	BLACK;
	p_VarList( prog->globals, 0 );
	p_Function( prog->fns, 0 );
}

void p_Function(
Function *fns,
int nest
)
{
	Function *next;

	next = fns;
	while( next ) {
		RED;
		printf("function name <%s>\n",next->name );
		BLACK;
		printf("params\n");
		p_VarList( next->params, nest+1 );
		/* VarList *params; */
		printf("is_static <%d>\n", next->is_static );
		printf("has_varargs <%d>\n", next->has_varargs );

		/* Node *node; */
		/* VarList *locals; */
		printf("stack_size <%d>\n", next->stack_size);

		//p_VarList( next->locals, nest+1 );
		next = next->next;
	}

}

void p_Var( Var *V, int nest ) {
	PS( nest )
	YELLOW;
	printf("<name>=%s",V->name);
	BLACK;
	PS(1);
	printf(" <is_local>=%d",V->is_local);
	PS(1);
	printf(" <offset>=%d",V->offset);
	PS(1);
	printf(" <is_static>=%d",V->is_static);
	printf("\n");
	p_Type( V->ty, nest );
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

void p_Type( Type *T, int nest ) {
	Type *base;
	PS( nest+1 );
	printf("<kind>=%s",pType(T->kind));
	PS(1);
	printf("<size>=%d",T->size);
	PS(1);
	printf("<align>=%d",T->align);
	PS(1);
	printf("<is_incomplete>=%d",T->is_incomplete);
	PS(1);
	printf("<array_len>=%d",T->array_len);
	printf("\n");
	base = T->base;
	while( base ) {
		p_Type( base, nest );
		base = base->base;
	}
	//PS(1);
	//printf("<*members>=%d\n",T->*members);
	//printf("<*return_ty>=%d\n",T->*return_ty);
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
