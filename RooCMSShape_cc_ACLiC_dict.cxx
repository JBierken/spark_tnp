// Do NOT change. Changes will be lost next time file is generated

#define R__DICTIONARY_FILENAME dIafsdIcerndOchdIuserdIjdIjbierkendIspark_tnpdIRooCMSShape_cc_ACLiC_dict
#define R__NO_DEPRECATION

/*******************************************************************/
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define G__DICTIONARY
#include "RConfig.h"
#include "TClass.h"
#include "TDictAttributeMap.h"
#include "TInterpreter.h"
#include "TROOT.h"
#include "TBuffer.h"
#include "TMemberInspector.h"
#include "TInterpreter.h"
#include "TVirtualMutex.h"
#include "TError.h"

#ifndef G__ROOT
#define G__ROOT
#endif

#include "RtypesImp.h"
#include "TIsAProxy.h"
#include "TFileMergeInfo.h"
#include <algorithm>
#include "TCollectionProxyInfo.h"
/*******************************************************************/

#include "TDataMember.h"

// The generated code does not explicitly qualifies STL entities
namespace std {} using namespace std;

// Header files passed as explicit arguments
#include "/afs/cern.ch/user/j/jbierken/spark_tnp/./RooCMSShape.cc"

// Header files passed via #pragma extra_include

   namespace ROOT {
      inline ::ROOT::TGenericClassInfo *GenerateInitInstance();
      static TClass *ROOT_Dictionary();

      // Function generating the singleton type initializer
      inline ::ROOT::TGenericClassInfo *GenerateInitInstance()
      {
         static ::ROOT::TGenericClassInfo 
            instance("ROOT", 0 /*version*/, "Rtypes.h", 107,
                     ::ROOT::Internal::DefineBehavior((void*)0,(void*)0),
                     &ROOT_Dictionary, 0);
         return &instance;
      }
      // Insure that the inline function is _not_ optimized away by the compiler
      ::ROOT::TGenericClassInfo *(*_R__UNIQUE_DICT_(InitFunctionKeeper))() = &GenerateInitInstance;  
      // Static variable to force the class initialization
      static ::ROOT::TGenericClassInfo *_R__UNIQUE_DICT_(Init) = GenerateInitInstance(); R__UseDummy(_R__UNIQUE_DICT_(Init));

      // Dictionary for non-ClassDef classes
      static TClass *ROOT_Dictionary() {
         return GenerateInitInstance()->GetClass();
      }

   }

namespace ROOT {
   static void *new_RooCMSShape(void *p = 0);
   static void *newArray_RooCMSShape(Long_t size, void *p);
   static void delete_RooCMSShape(void *p);
   static void deleteArray_RooCMSShape(void *p);
   static void destruct_RooCMSShape(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::RooCMSShape*)
   {
      ::RooCMSShape *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TInstrumentedIsAProxy< ::RooCMSShape >(0);
      static ::ROOT::TGenericClassInfo 
         instance("RooCMSShape", ::RooCMSShape::Class_Version(), "RooCMSShape.h", 32,
                  typeid(::RooCMSShape), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &::RooCMSShape::Dictionary, isa_proxy, 4,
                  sizeof(::RooCMSShape) );
      instance.SetNew(&new_RooCMSShape);
      instance.SetNewArray(&newArray_RooCMSShape);
      instance.SetDelete(&delete_RooCMSShape);
      instance.SetDeleteArray(&deleteArray_RooCMSShape);
      instance.SetDestructor(&destruct_RooCMSShape);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::RooCMSShape*)
   {
      return GenerateInitInstanceLocal((::RooCMSShape*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_DICT_(Init) = GenerateInitInstanceLocal((const ::RooCMSShape*)0x0); R__UseDummy(_R__UNIQUE_DICT_(Init));
} // end of namespace ROOT

//______________________________________________________________________________
atomic_TClass_ptr RooCMSShape::fgIsA(0);  // static to hold class pointer

//______________________________________________________________________________
const char *RooCMSShape::Class_Name()
{
   return "RooCMSShape";
}

//______________________________________________________________________________
const char *RooCMSShape::ImplFileName()
{
   return ::ROOT::GenerateInitInstanceLocal((const ::RooCMSShape*)0x0)->GetImplFileName();
}

//______________________________________________________________________________
int RooCMSShape::ImplFileLine()
{
   return ::ROOT::GenerateInitInstanceLocal((const ::RooCMSShape*)0x0)->GetImplFileLine();
}

//______________________________________________________________________________
TClass *RooCMSShape::Dictionary()
{
   fgIsA = ::ROOT::GenerateInitInstanceLocal((const ::RooCMSShape*)0x0)->GetClass();
   return fgIsA;
}

//______________________________________________________________________________
TClass *RooCMSShape::Class()
{
   if (!fgIsA.load()) { R__LOCKGUARD(gInterpreterMutex); fgIsA = ::ROOT::GenerateInitInstanceLocal((const ::RooCMSShape*)0x0)->GetClass(); }
   return fgIsA;
}

//______________________________________________________________________________
void RooCMSShape::Streamer(TBuffer &R__b)
{
   // Stream an object of class RooCMSShape.

   if (R__b.IsReading()) {
      R__b.ReadClassBuffer(RooCMSShape::Class(),this);
   } else {
      R__b.WriteClassBuffer(RooCMSShape::Class(),this);
   }
}

namespace ROOT {
   // Wrappers around operator new
   static void *new_RooCMSShape(void *p) {
      return  p ? new(p) ::RooCMSShape : new ::RooCMSShape;
   }
   static void *newArray_RooCMSShape(Long_t nElements, void *p) {
      return p ? new(p) ::RooCMSShape[nElements] : new ::RooCMSShape[nElements];
   }
   // Wrapper around operator delete
   static void delete_RooCMSShape(void *p) {
      delete ((::RooCMSShape*)p);
   }
   static void deleteArray_RooCMSShape(void *p) {
      delete [] ((::RooCMSShape*)p);
   }
   static void destruct_RooCMSShape(void *p) {
      typedef ::RooCMSShape current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::RooCMSShape

namespace {
  void TriggerDictionaryInitialization_RooCMSShape_cc_ACLiC_dict_Impl() {
    static const char* headers[] = {
"./RooCMSShape.cc",
0
    };
    static const char* includePaths[] = {
"/cvmfs/sft.cern.ch/lcg/releases/ROOT/v6.20.06-9e6ed/x86_64-centos7-gcc8-opt/include",
"/cvmfs/sft.cern.ch/lcg/views/LCG_97apython3/x86_64-centos7-gcc8-opt/src/cpp",
"/cvmfs/sft.cern.ch/lcg/views/LCG_97apython3/x86_64-centos7-gcc8-opt/include",
"/cvmfs/sft.cern.ch/lcg/releases/Python/3.7.6-b96a9/x86_64-centos7-gcc8-opt/include/python3.7m",
"/cvmfs/sft.cern.ch/lcg/releases/R/3.6.3-ca0ad/x86_64-centos7-gcc8-opt/lib64/R/include",
"/cvmfs/sft.cern.ch/lcg/releases/R/3.6.3-ca0ad/x86_64-centos7-gcc8-opt/lib64/R/library/RInside/include",
"/cvmfs/sft.cern.ch/lcg/releases/R/3.6.3-ca0ad/x86_64-centos7-gcc8-opt/lib64/R/library/Rcpp/include",
"/cvmfs/sft.cern.ch/lcg/views/LCG_97apython3/x86_64-centos7-gcc8-opt/include/Garfield",
"/cvmfs/sft.cern.ch/lcg/releases/ROOT/v6.20.06-9e6ed/x86_64-centos7-gcc8-opt/etc/",
"/cvmfs/sft.cern.ch/lcg/releases/ROOT/v6.20.06-9e6ed/x86_64-centos7-gcc8-opt/etc//cling",
"/cvmfs/sft.cern.ch/lcg/releases/ROOT/v6.20.06-9e6ed/x86_64-centos7-gcc8-opt/include/",
"/cvmfs/sft.cern.ch/lcg/releases/Python/3.7.6-b96a9/x86_64-centos7-gcc8-opt/include",
"/cvmfs/sft.cern.ch/lcg/releases/ROOT/v6.20.06-9e6ed/x86_64-centos7-gcc8-opt/include/",
"/afs/cern.ch/user/j/jbierken/spark_tnp/",
0
    };
    static const char* fwdDeclCode = R"DICTFWDDCLS(
#line 1 "RooCMSShape_cc_ACLiC_dict dictionary forward declarations' payload"
#pragma clang diagnostic ignored "-Wkeyword-compat"
#pragma clang diagnostic ignored "-Wignored-attributes"
#pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
extern int __Cling_Autoloading_Map;
class __attribute__((annotate(R"ATTRDUMP(file_name@@@/afs/cern.ch/user/j/jbierken/spark_tnp/./RooCMSShape.h)ATTRDUMP"))) __attribute__((annotate(R"ATTRDUMP(pattern@@@*)ATTRDUMP"))) __attribute__((annotate("$clingAutoload$RooCMSShape.h")))  __attribute__((annotate("$clingAutoload$./RooCMSShape.cc")))  RooCMSShape;
)DICTFWDDCLS";
    static const char* payloadCode = R"DICTPAYLOAD(
#line 1 "RooCMSShape_cc_ACLiC_dict dictionary payload"

#ifndef __ACLIC__
  #define __ACLIC__ 1
#endif

#define _BACKWARD_BACKWARD_WARNING_H
// Inline headers
#include "./RooCMSShape.cc"

#undef  _BACKWARD_BACKWARD_WARNING_H
)DICTPAYLOAD";
    static const char* classesHeaders[] = {
"", payloadCode, "@",
"ROOT::GenerateInitInstance", payloadCode, "@",
"RooCMSShape", payloadCode, "@",
"RooCMSShape::fgIsA", payloadCode, "@",
nullptr
};
    static bool isInitialized = false;
    if (!isInitialized) {
      TROOT::RegisterModule("RooCMSShape_cc_ACLiC_dict",
        headers, includePaths, payloadCode, fwdDeclCode,
        TriggerDictionaryInitialization_RooCMSShape_cc_ACLiC_dict_Impl, {}, classesHeaders, /*hasCxxModule*/false);
      isInitialized = true;
    }
  }
  static struct DictInit {
    DictInit() {
      TriggerDictionaryInitialization_RooCMSShape_cc_ACLiC_dict_Impl();
    }
  } __TheDictionaryInitializer;
}
void TriggerDictionaryInitialization_RooCMSShape_cc_ACLiC_dict() {
  TriggerDictionaryInitialization_RooCMSShape_cc_ACLiC_dict_Impl();
}
