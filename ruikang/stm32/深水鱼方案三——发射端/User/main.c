#include "stm32f10x.h"
#include "bsp_gpio.h"
#include "bsp_GeneralTim.h"
#include "bsp_usart.h"


#include <stdio.h>
#include <string.h>

uint16_t time = 0xFFFF;																															//时间变量

//GPIO定义区
#define KEY1 PAin(0)
#define KEY2 PCin(13)
#define KEY3 PCin(4)
#define KEY4 PCin(5)
#define LED_R PBout(5)
#define LED_G PBout(0)
#define LED_B PBout(1)

uint16_t volatile CCR1_Val = 750;
uint16_t volatile CCR2_Val = 750;

extern uint8_t config_complete[Array_Length];																				//初始化完成
extern uint8_t self_check_enable;																										//初始化控制字
extern uint32_t watchdog_delay;
extern uint8_t sleep_warning[Array_Length];																					//休眠警告

void Delay(__IO u32 nCount);

/**
  * @brief  主函数
  * @param  无  
  * @retval 无
  */
int main(void)
{
	GPIO_Config();																																		//初始化GPIO				配置模式为 推挽
	USART_Config();																																		//初始化USART			配置模式为 115200 8-N-1，中断接收
	USART2_Config();
	USART3_Config();
	GENERAL_TIM_Init();																																//初始化双路TIM   	配置模式为 复用浮空输出
	TIM_Cmd(GENERAL_TIM2, DISABLE);
	while(1)
	{
		if(watchdog_delay > 30000)
		{
			Usart_SendArray(USART2,sleep_warning,Array_Length);
			while(watchdog_delay > 30000);
		}
			
	}
}

/**延迟发生器
	*具体功能：简单延迟
	*输入参数：一个32位的数
	*返回参数：
	*涉及操作：
	*/
void Delay(__IO uint32_t nCount)
{
	for(; nCount != 0; nCount--);
}

/*********************************************END OF FILE**********************/
