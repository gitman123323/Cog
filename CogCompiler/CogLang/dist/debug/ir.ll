; ModuleID = "main"
target triple = "x86_64-pc-windows-msvc"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

@"true" = constant i1 1
@"false" = constant i1 0
define i32 @"add"(i32 %".1", i32 %".2")
{
add_entry:
  %".4" = alloca i32
  store i32 %".1", i32* %".4"
  %".6" = alloca i32
  store i32 %".2", i32* %".6"
  %".8" = load i32, i32* %".4"
  %".9" = load i32, i32* %".6"
  %".10" = add i32 %".8", %".9"
  ret i32 %".10"
}

define float @"add_float"(float %".1", float %".2")
{
add_float_entry:
  %".4" = alloca float
  store float %".1", float* %".4"
  %".6" = alloca float
  store float %".2", float* %".6"
  %".8" = load float, float* %".4"
  %".9" = load float, float* %".6"
  %".10" = fadd float %".8", %".9"
  ret float %".10"
}

define void @"display_family"()
{
display_family_entry:
  %".2" = bitcast [7 x i8]* @"__str_1" to i8*
  %".3" = alloca i8*
  store i8* %".2", i8** %".3"
  %".5" = bitcast [4 x i8]* @"__str_2" to i8*
  %".6" = alloca i8*
  store i8* %".5", i8** %".6"
  %".8" = bitcast [4 x i8]* @"__str_3" to i8*
  %".9" = alloca i8*
  store i8* %".8", i8** %".9"
  %".11" = bitcast [5 x i8]* @"__str_4" to i8*
  %".12" = alloca i8*
  store i8* %".11", i8** %".12"
  %".14" = bitcast [6 x i8]* @"__str_5" to i8*
  %".15" = alloca i8*
  store i8* %".14", i8** %".15"
  %".17" = alloca float
  store float 0x3ff8000000000000, float* %".17"
  %".19" = load float, float* %".17"
  store float 0x404535c280000000, float* %".17"
  %".21" = load float, float* %".17"
  %".22" = sitofp i32 49 to float
  %".23" = fmul float %".21", %".22"
  store float %".23", float* %".17"
  %".25" = alloca float
  store float 0x40452a3d80000000, float* %".25"
  %".27" = alloca float
  store float 0x40091eb860000000, float* %".27"
  %".29" = alloca float
  store float 0x40091eb860000000, float* %".29"
  %".31" = bitcast [27 x i8]* @"__str_6" to i8*
  %".32" = load float, float* %".29"
  %".33" = fpext float %".32" to double
  %".34" = load float, float* %".27"
  %".35" = fpext float %".34" to double
  %".36" = bitcast [26 x i8]* @"__str_7" to i8*
  %".37" = call i32 (i8*, ...) @"printf"(i8* %".36", double %".33", double %".35")
  ret void
}

@"__str_1" = internal constant [7 x i8] c"Loghan\00"
@"__str_2" = internal constant [4 x i8] c"Mom\00"
@"__str_3" = internal constant [4 x i8] c"Dad\00"
@"__str_4" = internal constant [5 x i8] c"Eden\00"
@"__str_5" = internal constant [6 x i8] c"Livia\00"
@"__str_6" = internal constant [27 x i8] c"The values are {z} and {y}\00"
@"__str_7" = internal constant [26 x i8] c"The values are %f and %f\0a\00"
define i1 @"hello_world"()
{
hello_world_entry:
  ret i1 1
}

define i32 @"main"()
{
main_entry:
  %".2" = bitcast [7 x i8]* @"__str_8" to i8*
  %".3" = alloca i8*
  store i8* %".2", i8** %".3"
  %".5" = bitcast [5 x i8]* @"__str_9" to i8*
  %".6" = alloca i8*
  store i8* %".5", i8** %".6"
  %".8" = alloca i1
  store i1 0, i1* %".8"
  %".10" = alloca i32
  store i32 1, i32* %".10"
  %".12" = icmp eq i32 1, 2
  %".13" = alloca i1
  store i1 %".12", i1* %".13"
  %".15" = bitcast [30 x i8]* @"__str_10" to i8*
  %".16" = load i8*, i8** %".3"
  %".17" = bitcast [27 x i8]* @"__str_11" to i8*
  %".18" = call i32 (i8*, ...) @"printf"(i8* %".17", i8* %".16")
  %".19" = load i32, i32* %".10"
  %".20" = add i32 %".19", 590
  store i32 %".20", i32* %".10"
  %".22" = bitcast [12 x i8]* @"__str_12" to i8*
  %".23" = load i32, i32* %".10"
  %".24" = bitcast [12 x i8]* @"__str_13" to i8*
  %".25" = call i32 (i8*, ...) @"printf"(i8* %".24", i32 %".23")
  %".26" = load i32, i32* %".10"
  %".27" = call i32 @"add"(i32 %".26", i32 60)
  %".28" = alloca i32
  store i32 %".27", i32* %".28"
  %".30" = bitcast [19 x i8]* @"__str_14" to i8*
  %".31" = load i32, i32* %".28"
  %".32" = bitcast [15 x i8]* @"__str_15" to i8*
  %".33" = call i32 (i8*, ...) @"printf"(i8* %".32", i32 %".31")
  %".34" = alloca i32
  store i32 1, i32* %".34"
  br label %"for_loop_entry_16"
for_loop_entry_16:
  %".37" = load i32, i32* %".34"
  %".38" = icmp eq i32 %".37", 7
  br i1 %".38", label %"for_loop_entry_16.if", label %"for_loop_entry_16.endif"
for_loop_otherwise_16:
  %".58" = load i1, i1* %".8"
  %".59" = icmp eq i1 %".58", 1
  br i1 %".59", label %"for_loop_otherwise_16.if", label %"for_loop_otherwise_16.endif"
for_loop_entry_16.if:
  %".40" = load i1, i1* %".8"
  store i1 1, i1* %".8"
  br label %"for_loop_entry_16.endif"
for_loop_entry_16.endif:
  %".43" = load i32, i32* %".34"
  %".44" = icmp eq i32 %".43", 8
  br i1 %".44", label %"for_loop_entry_16.endif.if", label %"for_loop_entry_16.endif.endif"
for_loop_entry_16.endif.if:
  br label %"for_loop_otherwise_16"
for_loop_entry_16.endif.endif:
  %".47" = bitcast [18 x i8]* @"__str_17" to i8*
  %".48" = load i32, i32* %".34"
  %".49" = bitcast [18 x i8]* @"__str_18" to i8*
  %".50" = call i32 (i8*, ...) @"printf"(i8* %".49", i32 %".48")
  %".51" = load i32, i32* %".34"
  %".52" = add i32 %".51", 1
  %".53" = load i32, i32* %".34"
  store i32 %".52", i32* %".34"
  %".55" = load i32, i32* %".34"
  %".56" = icmp slt i32 %".55", 10
  br i1 %".56", label %"for_loop_entry_16", label %"for_loop_otherwise_16"
for_loop_otherwise_16.if:
  call void @"display_family"()
  br label %"for_loop_otherwise_16.endif"
for_loop_otherwise_16.endif:
  %".63" = load i32, i32* %".34"
  ret i32 %".63"
}

@"__str_8" = internal constant [7 x i8] c"Loghan\00"
@"__str_9" = internal constant [5 x i8] c"Eden\00"
@"__str_10" = internal constant [30 x i8] c"hello {name}! Welcome to Cog.\00"
@"__str_11" = internal constant [27 x i8] c"hello %s! Welcome to Cog.\0a\00"
@"__str_12" = internal constant [12 x i8] c"i * 3 = {j}\00"
@"__str_13" = internal constant [12 x i8] c"i * 3 = %d\0a\00"
@"__str_14" = internal constant [19 x i8] c"j * shit = {total}\00"
@"__str_15" = internal constant [15 x i8] c"j * shit = %d\0a\00"
@"__str_17" = internal constant [18 x i8] c"Counting i = {i}\0a\00"
@"__str_18" = internal constant [18 x i8] c"Counting i = %d\0a\0a\00"